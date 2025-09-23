"""Main FastAPI application instance."""

from __future__ import annotations

from fastapi import FastAPI

from src.app.api.v1 import api_router
from src.app.core import settings
from src.app.db.session import SessionLocal
from src.app.db.utils import create_all_tables
from src.app.services.users import user_service

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def _on_startup() -> None:
    """Initialise database tables and default roles on application startup."""

    create_all_tables()
    session = SessionLocal()
    try:
        user_service.ensure_default_roles(session)
    finally:
        session.close()


__all__ = ["app"]
