"""
API v1 router
"""

from fastapi import APIRouter

# Import route modules
from .endpoints import brands, monitoring, alerts, analytics

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(brands.router, prefix="/brands", tags=["brands"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
