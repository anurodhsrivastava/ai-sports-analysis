"""
Sports Router
GET  /sports          - List available sports
POST /sports/wishlist - Add sport to wishlist for notifications
"""

import json
import time

from fastapi import APIRouter

from ..config import settings
from ..models.schemas import WishlistRequest, WishlistResponse
from ..sports.registry import SportRegistry

router = APIRouter(prefix="/api", tags=["sports"])


@router.get("/sports")
async def list_sports():
    """Return all registered sports."""
    return SportRegistry.list_sports()


@router.post("/sports/wishlist", response_model=WishlistResponse)
async def add_to_wishlist(request: WishlistRequest):
    """Add a sport to the user wishlist.

    Stores the request so admins can see demand for unsupported sports.
    """
    wishlist_dir = settings.wishlist_dir
    wishlist_dir.mkdir(parents=True, exist_ok=True)

    entry = {
        "sport": request.sport,
        "email": request.email,
        "timestamp": time.time(),
    }

    wishlist_file = wishlist_dir / "wishlist.jsonl"
    with open(wishlist_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return WishlistResponse(
        success=True,
        message=f"Thanks! We'll notify you when {request.sport} analysis becomes available.",
    )
