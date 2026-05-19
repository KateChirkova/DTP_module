#!/usr/bin/env python3
# CLI: новый пользователь при совпадении DTP_USER_CREATE_SECRET
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.traffic_dtp.db.models.user import User
from src.traffic_dtp.db.session import SessionLocal
from src.traffic_dtp.services.auth import hash_password


def main() -> None:
    expected_secret = (os.getenv("DTP_USER_CREATE_SECRET") or "").strip()
    if not expected_secret:
        print(
            "Отказ: не задан DTP_USER_CREATE_SECRET. "
            "Для первого админа используйте DTP_BOOTSTRAP_LOGIN/PASSWORD/ADMIN=1 в compose "
            "или задайте секрет только на сервере.",
            file=sys.stderr,
        )
        sys.exit(1)

    p = argparse.ArgumentParser(description="Добавить пользователя (нужен DTP_USER_CREATE_SECRET).")
    p.add_argument("--login", required=True, help="логин")
    p.add_argument("--password", required=True, help="пароль")
    p.add_argument("--admin", action="store_true", help="выдать права администратора")
    p.add_argument("--secret", required=True, help="должен совпадать с DTP_USER_CREATE_SECRET")
    p.add_argument(
        "--replace",
        action="store_true",
        help="если логин уже есть — удалить и создать заново",
    )
    args = p.parse_args()

    if args.secret != expected_secret:
        print("Неверный --secret.", file=sys.stderr)
        sys.exit(1)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.login == args.login).first()
        if existing:
            if not args.replace:
                print(
                    f"Пользователь {args.login!r} уже есть. Укажите --replace или другой --login.",
                    file=sys.stderr,
                )
                sys.exit(1)
            db.delete(existing)
            db.commit()
            print("Старый пользователь удалён (--replace).")

        db.add(
            User(
                login=args.login,
                password_hash=hash_password(args.password),
                is_admin=args.admin,
            )
        )
        db.commit()
        role = "администратор" if args.admin else "пользователь"
        print(f"Создан {role} login={args.login!r}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
