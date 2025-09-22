"""Service helpers for user and RBAC management."""

from __future__ import annotations

from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.models import Permission, Role, User
from src.app.models.role import role_permissions
from src.app.models.user import user_roles
from src.app.services.auth import auth_service

_ROLE_PRESETS: dict[str, dict[str, Sequence[str]]] = {
    "admin": {"permissions": ("auth:login", "auth:refresh", "users:manage")},
    "manager": {"permissions": ("auth:login", "missions:manage")},
    "tech": {"permissions": ("auth:login", "missions:execute")},
    "viewer": {"permissions": ("auth:login", "missions:view")},
}

_PERMISSION_DESCRIPTIONS: dict[str, str] = {
    "auth:login": "Allow authentication via email/password.",
    "auth:refresh": "Allow refreshing access tokens.",
    "users:manage": "Manage user accounts and roles.",
    "missions:manage": "Manage missions and planning data.",
    "missions:execute": "Execute missions assigned to the technician.",
    "missions:view": "View missions and planning information.",
}


class UserService:
    """Encapsulate business logic for user and role management."""

    def ensure_default_roles(self, session: Session) -> None:
        """Ensure the minimal set of roles and permissions exists."""

        for perm_name, description in _PERMISSION_DESCRIPTIONS.items():
            existing = session.execute(select(Permission).where(Permission.name == perm_name)).scalar_one_or_none()
            if existing is None:
                session.add(Permission(name=perm_name, description=description))

        session.flush()

        for role_name, preset in _ROLE_PRESETS.items():
            role = session.execute(select(Role).where(Role.name == role_name)).scalar_one_or_none()
            if role is None:
                role = Role(name=role_name)
                session.add(role)
                session.flush([role])

            permissions = list(self._get_permissions(session, preset.get("permissions", ())))
            role.permissions = permissions

        session.commit()

    def create_user(self, session: Session, email: str, password: str, roles: Iterable[str] | None = None) -> User:
        """Create a new user with the provided credentials."""

        hashed = auth_service.hash_password(password)
        user = User(email=email, hashed_password=hashed)
        session.add(user)
        session.flush([user])

        if roles:
            attached_roles = [self._get_or_create_role(session, role_name) for role_name in roles]
            user.roles = attached_roles

        session.commit()
        session.refresh(user)
        return user

    def get_by_email(self, session: Session, email: str) -> User | None:
        """Return a user by email."""

        return session.execute(select(User).where(User.email == email)).scalar_one_or_none()

    def _get_permissions(self, session: Session, names: Iterable[str]) -> Iterable[Permission]:
        for name in names:
            permission = session.execute(select(Permission).where(Permission.name == name)).scalar_one_or_none()
            if permission is None:
                permission = Permission(name=name, description=_PERMISSION_DESCRIPTIONS.get(name))
                session.add(permission)
                session.flush([permission])
            yield permission

    def _get_or_create_role(self, session: Session, name: str) -> Role:
        role = session.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
        if role is None:
            role = Role(name=name)
            session.add(role)
            session.flush([role])
        return role

    def list_role_names(self, user: User) -> list[str]:
        """Return the list of role names for the provided user."""

        return [role.name for role in user.roles]


def detach_user_relationships(session: Session) -> None:
    """Helper to clear association tables (useful for tests)."""

    session.execute(user_roles.delete())
    session.execute(role_permissions.delete())
    session.commit()


user_service = UserService()


__all__ = ["UserService", "user_service", "detach_user_relationships"]
