# лёгкие миграции SQLite без Alembic
from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def ensure_user_is_admin_column(engine: Engine) -> None:
    inspector = inspect(engine)
    if "user" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("user")}
    if "is_admin" in columns:
        return
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE user ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0"))
    print("[schema] user.is_admin добавлен")


# переход на общую модель: одно уведомление на accident_id + notification_reads
def ensure_shared_notifications_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "notifications" not in tables:
        return

    if "notification_reads" not in tables:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    CREATE TABLE notification_reads (
                        id INTEGER NOT NULL PRIMARY KEY,
                        notification_id INTEGER NOT NULL,
                        user_login VARCHAR(50) NOT NULL,
                        read_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        FOREIGN KEY(notification_id) REFERENCES notifications (id) ON DELETE CASCADE,
                        FOREIGN KEY(user_login) REFERENCES user (login),
                        CONSTRAINT uq_notification_read_user UNIQUE (notification_id, user_login)
                    )
                    """
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_notification_reads_notification_id "
                    "ON notification_reads (notification_id)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_notification_reads_user_login "
                    "ON notification_reads (user_login)"
                )
            )
        print("[schema] notification_reads создана")

    columns = {col["name"] for col in inspector.get_columns("notifications")}
    if "user_login" not in columns:
        return

    print("[schema] миграция notifications -> одна запись на ДТП + notification_reads")
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                "SELECT id, accident_id, user_login, status, created_at "
                "FROM notifications ORDER BY accident_id, id"
            )
        ).fetchall()

        keepers: dict[int, int] = {}
        for row in rows:
            acc_id = row.accident_id
            if acc_id not in keepers:
                keepers[acc_id] = row.id

        for row in rows:
            keeper_id = keepers[row.accident_id]
            if row.status != "read":
                continue
            conn.execute(
                text(
                    """
                    INSERT OR IGNORE INTO notification_reads
                        (notification_id, user_login, read_at)
                    VALUES (:nid, :login, COALESCE(:read_at, CURRENT_TIMESTAMP))
                    """
                ),
                {"nid": keeper_id, "login": row.user_login, "read_at": row.created_at},
            )

        keeper_ids = list(keepers.values())
        if keeper_ids:
            placeholders = ", ".join(str(i) for i in keeper_ids)
            conn.execute(text(f"DELETE FROM notifications WHERE id NOT IN ({placeholders})"))

        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS notifications_new (
                    id INTEGER NOT NULL PRIMARY KEY,
                    accident_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(accident_id) REFERENCES accidents (id),
                    CONSTRAINT uq_notifications_accident_id UNIQUE (accident_id)
                )
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT OR IGNORE INTO notifications_new (id, accident_id, created_at)
                SELECT id, accident_id, created_at FROM notifications
                """
            )
        )
        conn.execute(text("DROP TABLE notifications"))
        conn.execute(text("ALTER TABLE notifications_new RENAME TO notifications"))

    print("[schema] notifications: общая модель применена")
