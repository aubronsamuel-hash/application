"""Database session handling utilities."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.app.core.config import settings

_connect_args: dict[str, object] = {}
if settings.database_url.startswith("sqlite"):  # pragma: no cover - branch ensures sqlite compatibility
    _connect_args["check_same_thread"] = False

engine = create_engine(settings.database_url, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session for FastAPI dependencies."""

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


__all__ = ["SessionLocal", "engine", "get_session"]
