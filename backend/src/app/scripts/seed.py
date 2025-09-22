"""Seed script for creating a default admin user."""

from __future__ import annotations

from src.app.core import settings
from src.app.db.session import SessionLocal
from src.app.db.utils import create_all_tables
from src.app.services.users import user_service

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin"


def main() -> None:
    """Seed the database with an admin user if none exists."""

    create_all_tables()
    session = SessionLocal()
    try:
        user_service.ensure_default_roles(session)
        existing = user_service.get_by_email(session, ADMIN_EMAIL)
        if existing is None:
            user_service.create_user(session, ADMIN_EMAIL, ADMIN_PASSWORD, roles=["admin"])
            print(f"Admin user created: {ADMIN_EMAIL}")  # noqa: T201 - script feedback
        else:
            print("Admin user already exists")  # noqa: T201 - script feedback
    finally:
        session.close()


if __name__ == "__main__":
    print(f"Using database: {settings.database_url}")  # noqa: T201 - script feedback
    main()
