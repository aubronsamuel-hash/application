from fastapi import FastAPI

from .api.v1.health import router as health_router


app = FastAPI(title="Codex API", version="0.1.0")
app.include_router(health_router, prefix="/api/v1")


__all__ = ["app"]
