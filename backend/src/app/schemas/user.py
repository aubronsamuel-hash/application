"""Pydantic schemas for user responses."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RoleRead(BaseModel):
    """Public representation of a role."""

    model_config = ConfigDict(from_attributes=True)

    name: str


class UserRead(BaseModel):
    """Public representation of a user."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_active: bool
    roles: list[RoleRead] = Field(default_factory=list)


__all__ = ["RoleRead", "UserRead"]
