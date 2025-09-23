"""Test fixtures for backend authentication tests."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_PATH = ROOT_DIR / "src"
for candidate in (ROOT_DIR, SRC_PATH):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from src.app.db.base import Base  # noqa: E402
from src.app.db.session import get_session  # noqa: E402
from src.app.main import app  # noqa: E402
from src.app.services.users import user_service  # noqa: E402

TEST_DATABASE_URL = "sqlite:///:memory:"


def _create_engine():
    connect_args = {"check_same_thread": False} if TEST_DATABASE_URL.startswith("sqlite") else {}
    pool_kwargs = {"poolclass": StaticPool} if TEST_DATABASE_URL.startswith("sqlite") else {}
    return create_engine(TEST_DATABASE_URL, connect_args=connect_args, **pool_kwargs)


@pytest.fixture(scope="session")
def engine() -> Generator:
    engine = _create_engine()
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(engine) -> Generator[Session, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = TestingSessionLocal()
    user_service.ensure_default_roles(session)
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def _override_get_session() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            db_session.rollback()

    app.dependency_overrides[get_session] = _override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_session, None)


@pytest.fixture()
def create_user(db_session: Session):
    def _create(email: str, password: str, roles: list[str]) -> None:
        user_service.create_user(db_session, email, password, roles=roles)
    return _create
