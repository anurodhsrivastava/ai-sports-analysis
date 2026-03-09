"""Sports router — lists available sports."""

from fastapi import APIRouter

from ..sports.registry import SportRegistry

router = APIRouter(prefix="/api", tags=["sports"])


@router.get("/sports")
async def list_sports():
    """Return all registered sports."""
    return SportRegistry.list_sports()
