"""
Brand management API endpoints
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_brands():
    """Get all brands"""
    return {"message": "Brands endpoint - under development"}
