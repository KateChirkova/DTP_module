# первый пользователь из DTP_BOOTSTRAP_* при старте API
from __future__ import annotations

import os

from src.traffic_dtp.db.models.user import User
from src.traffic_dtp.db.session import SessionLocal
from src.traffic_dtp.services.auth import hash_password


def bootstrap_user_from_env() -> None:
    login = (os.getenv("DTP_BOOTSTRAP_LOGIN") or "").strip()
    raw = os.getenv("DTP_BOOTSTRAP_PASSWORD")
    if not login or raw is None:
        return

    password = str(raw)
    if not password:
        return

    is_admin = (os.getenv("DTP_BOOTSTRAP_ADMIN") or "").strip().lower() in ("1", "true", "yes")

    db = SessionLocal()
    try:
        if db.query(User).filter(User.login == login).first() is not None:
            return
        db.add(
            User(
                login=login,
                password_hash=hash_password(password),
                is_admin=is_admin,
            )
        )
        db.commit()
        role = "администратор" if is_admin else "пользователь"
        print(f"[bootstrap] создан {role} {login!r} (из DTP_BOOTSTRAP_*)")
    finally:
        db.close()
