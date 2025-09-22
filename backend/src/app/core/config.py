"""Application configuration primitives."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(slots=True)
class Settings:
    """Runtime configuration resolved from environment variables."""

    app_name: str = "Codex API"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///./codex.db"
    jwt_secret: str = "change_me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60

    @classmethod
    def from_env(cls) -> "Settings":
        """Build a :class:`Settings` instance using environment variables."""

        defaults = cls()
        database_url = os.getenv("DATABASE_URL") or defaults.database_url
        jwt_secret = os.getenv("JWT_SECRET") or defaults.jwt_secret
        jwt_algorithm = os.getenv("JWT_ALGORITHM") or defaults.jwt_algorithm
        access_expire = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", defaults.access_token_expire_minutes))
        refresh_expire = int(os.getenv("JWT_REFRESH_EXPIRE_MINUTES", defaults.refresh_token_expire_minutes))
        return cls(
            app_name=os.getenv("APP_NAME", defaults.app_name),
            app_version=os.getenv("APP_VERSION", defaults.app_version),
            database_url=database_url,
            jwt_secret=jwt_secret,
            jwt_algorithm=jwt_algorithm,
            access_token_expire_minutes=access_expire,
            refresh_token_expire_minutes=refresh_expire,
        )


settings = Settings.from_env()


__all__ = ["Settings", "settings"]
