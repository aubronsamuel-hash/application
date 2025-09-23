"""Codex backend application package."""

from __future__ import annotations

from importlib import import_module

# Ensure ORM models are discoverable via `from src.app import models`.
models = import_module("src.app.models")

__all__ = ["models"]
