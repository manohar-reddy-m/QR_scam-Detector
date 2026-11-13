"""
System endpoints — health check.
"""
import platform
import sys
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    python_version: str
    platform: str
    service: str
    version: str


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check():
    """Returns service health status."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        python_version=sys.version,
        platform=platform.platform(),
        service="QR Sentinel",
        version="1.0.0",
    )
