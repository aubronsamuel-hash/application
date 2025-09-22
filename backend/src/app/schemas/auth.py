"""Pydantic schemas for authentication payloads."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    """Request body for the login endpoint."""

    email: str = Field(..., examples=["admin@example.com"])
    password: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    """Request body for refreshing an access token."""

    refresh_token: str = Field(..., min_length=10)


class TokenPair(BaseModel):
    """Response returned after a successful authentication or refresh."""

    model_config = ConfigDict(extra="ignore")

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


__all__ = ["LoginRequest", "RefreshRequest", "TokenPair"]
