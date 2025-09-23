"""Authentication API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.app.api.deps import get_current_user
from src.app.db.session import get_session
from src.app.models import User
from src.app.schemas.auth import LoginRequest, RefreshRequest, TokenPair
from src.app.schemas.user import UserRead
from src.app.services.auth import AuthError, auth_service
from src.app.services.users import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair, summary="Authenticate a user with email and password")
def login(payload: LoginRequest, session: Session = Depends(get_session)) -> TokenPair:
    """Authenticate a user and return a token pair."""

    user = user_service.get_by_email(session, payload.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    roles = user_service.list_role_names(user)
    if not roles:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User has no roles")

    if not auth_service.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token_pair = auth_service.create_token_pair(user.email, roles)
    return TokenPair(**token_pair)


@router.post("/refresh", response_model=TokenPair, summary="Refresh an access token")
def refresh(payload: RefreshRequest, session: Session = Depends(get_session)) -> TokenPair:
    """Refresh the access token using a refresh token."""

    try:
        token_payload = auth_service.decode_token(payload.refresh_token, expected_type="refresh")
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    subject = token_payload.get("sub")
    if subject is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = user_service.get_by_email(session, subject)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or unknown user")

    roles = user_service.list_role_names(user)
    token_pair = auth_service.create_token_pair(user.email, roles)
    return TokenPair(**token_pair)


@router.get("/me", response_model=UserRead, summary="Return the current authenticated user")
def read_profile(current_user: User = Depends(get_current_user)) -> UserRead:
    """Return details for the currently authenticated user."""

    return UserRead.model_validate(current_user)


__all__ = ["router"]
