"""Authentication helpers for hashing and token management."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.app.core.config import settings


class AuthError(RuntimeError):
    """Raised when an authentication operation fails."""


class AuthService:
    """Provide password hashing and JWT helpers."""

    def __init__(self) -> None:
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """Return a bcrypt hash for the provided password."""

        return self._pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify that the provided password matches the stored hash."""

        return self._pwd_context.verify(plain_password, hashed_password)

    def _create_token(
        self,
        subject: str,
        token_type: str,
        expires_delta: timedelta,
        payload: dict[str, Any] | None = None,
    ) -> str:
        issued_at = datetime.now(tz=timezone.utc)
        expire = issued_at + expires_delta
        to_encode: dict[str, Any] = {
            "sub": subject,
            "type": token_type,
            "exp": expire,
            "iat": issued_at,
            "jti": uuid4().hex,
        }
        if payload:
            to_encode.update(payload)
        return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    def create_access_token(self, subject: str, roles: list[str]) -> str:
        """Generate an access token embedding the user roles."""

        expires = timedelta(minutes=settings.access_token_expire_minutes)
        return self._create_token(subject, "access", expires, {"roles": roles})

    def create_refresh_token(self, subject: str) -> str:
        """Generate a refresh token for the provided subject."""

        expires = timedelta(minutes=settings.refresh_token_expire_minutes)
        return self._create_token(subject, "refresh", expires)

    def decode_token(self, token: str, expected_type: str | None = None) -> dict[str, Any]:
        """Decode a JWT token and optionally validate its type."""

        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        except JWTError as exc:  # pragma: no cover - jose raises multiple subclasses we treat the same way
            raise AuthError("Invalid token") from exc

        token_type = payload.get("type")
        if expected_type and token_type != expected_type:
            raise AuthError("Invalid token type")

        return payload

    def create_token_pair(self, subject: str, roles: list[str]) -> dict[str, str]:
        """Return a pair of access and refresh tokens."""

        access = self.create_access_token(subject, roles)
        refresh = self.create_refresh_token(subject)
        return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


auth_service = AuthService()


__all__ = ["AuthError", "AuthService", "auth_service"]
