"""
Alerts API endpoints
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_alerts():
    """Get all alerts"""
    return {"message": "Alerts endpoint - under development"}
