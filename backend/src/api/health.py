"""
Health Check Endpoint - Monitor application status.

Provides health check for monitoring and load balancing.
"""

from fastapi import APIRouter, status
from datetime import datetime
from typing import Dict, Any

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring.
    
    Returns application status and uptime information.
    
    **Returns:**
    - 200: Application is healthy
    
    **Response includes:**
    - status: "healthy" or "unhealthy"
    - timestamp: Current server time
    - version: Application version
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "turistando-api",
    }


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check - indicates if app is ready to serve traffic.
    
    Returns:
        Dict with readiness status
    """
    # In a production app, you would check database connectivity,
    # cache availability, etc. For now, we always return ready.
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check - indicates if app is running.
    
    Returns:
        Dict with liveness status
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }
