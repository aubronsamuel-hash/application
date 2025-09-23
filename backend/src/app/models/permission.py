"""Permission model definition."""

from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class Permission(Base):
    """Represents a granular permission assigned to roles."""

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")

    def __repr__(self) -> str:  # pragma: no cover - repr helpers used for debugging
        return f"Permission(id={self.id!r}, name={self.name!r})"


__all__ = ["Permission"]
