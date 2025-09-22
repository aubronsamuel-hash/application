from fastapi import APIRouter


router = APIRouter()


@router.get("/health", tags=["health"], summary="Return service health status")
def get_health() -> dict[str, str]:
    """Return a simple health payload for monitoring."""
    return {"status": "ok"}


__all__ = ["router"]
