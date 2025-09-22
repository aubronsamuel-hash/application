"""Reusable FastAPI dependencies for authentication and RBAC."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.app.db.session import get_session
from src.app.models import User
from src.app.services.auth import AuthError, auth_service
from src.app.services.users import user_service

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    """Return the authenticated user from the provided bearer token."""

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials
    try:
        payload = auth_service.decode_token(token, expected_type="access")
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = user_service.get_by_email(session, subject)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or unknown user")

    return user


def require_roles(*roles: str) -> Callable[[User], User]:
    """Dependency factory ensuring the current user owns one of the provided roles."""

    required = {role.lower() for role in roles}

    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        user_roles = {role.name.lower() for role in current_user.roles}
        if required and required.isdisjoint(user_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing required role")
        return current_user

    return _dependency


__all__ = ["get_current_user", "require_roles"]
