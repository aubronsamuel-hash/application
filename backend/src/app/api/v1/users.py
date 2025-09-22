"""User API endpoints with RBAC enforcement."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from src.app.api.deps import get_current_user, require_roles
from src.app.models import User
from src.app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead, summary="Return the currently authenticated user")
def read_current_user(current_user: User = Depends(get_current_user)) -> UserRead:
    """Return details of the logged-in user."""

    return UserRead.model_validate(current_user)


@router.get(
    "/admin/pulse",
    response_model=dict[str, str],
    summary="Admin-only heartbeat endpoint",
    dependencies=[Depends(require_roles("admin"))],
)
def admin_pulse() -> dict[str, str]:
    """Demonstrate RBAC by requiring the admin role."""

    return {"status": "admin-ok"}


__all__ = ["router"]
