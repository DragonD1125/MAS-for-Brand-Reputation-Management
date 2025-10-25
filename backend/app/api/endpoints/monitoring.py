"""
Monitoring API endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from pydantic import BaseModel

# Mock orchestrator reference for now
orchestrator = None

router = APIRouter()


class MonitoringRequest(BaseModel):
    brand_id: str
    platforms: List[str]
    keywords: List[str]
    timeframe: str = "1h"


class MonitoringResponse(BaseModel):
    status: str
    correlation_id: str
    message: str


@router.post("/start", response_model=MonitoringResponse)
async def start_monitoring(request: MonitoringRequest):
    """Start a brand monitoring cycle"""
    try:
        if not orchestrator:
            return MonitoringResponse(
                status="error",
                correlation_id="",
                message="Agent orchestrator not available"
            )
        
        brand_config = {
            "brand_id": request.brand_id,
            "platforms": request.platforms,
            "keywords": request.keywords,
            "timeframe": request.timeframe
        }
        
        correlation_id = await orchestrator.initiate_monitoring_cycle(brand_config)
        
        return MonitoringResponse(
            status="success",
            correlation_id=correlation_id,
            message=f"Monitoring cycle initiated for brand {request.brand_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_monitoring_status():
    """Get overall monitoring system status"""
    try:
        if not orchestrator:
            return {"status": "unavailable", "message": "Agent orchestrator not available"}
        
        return orchestrator.get_system_status()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def get_agent_status():
    """Get status of all agents"""
    try:
        if not orchestrator:
            return {"status": "unavailable", "agents": []}
        
        return orchestrator.get_system_status()["agents"]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_system_metrics():
    """Get system performance metrics"""
    try:
        if not orchestrator:
            return {"status": "unavailable", "metrics": {}}
        
        return orchestrator.get_agent_metrics()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """System health check"""
    try:
        if not orchestrator:
            return {
                "status": "unhealthy",
                "reason": "Agent orchestrator not available"
            }
        
        return await orchestrator.health_check()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
