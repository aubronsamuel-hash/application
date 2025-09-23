"""Helpers for database lifecycle management."""

from __future__ import annotations

from src.app.db.base import Base
from src.app.db.session import engine


def create_all_tables() -> None:
    """Create all database tables registered on the declarative base."""

    # Import models to ensure their metadata is registered before creating tables.
    from src.app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


__all__ = ["create_all_tables"]
