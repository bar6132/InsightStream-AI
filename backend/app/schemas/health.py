from pydantic import BaseModel
from typing import Dict, Optional, Any
from datetime import datetime


class ServiceHealthStatus(BaseModel):
    status: str  # "healthy" or "unhealthy"
    service: str
    timestamp: datetime
    error: Optional[str] = None
    points_count: Optional[int] = None
    available: Optional[bool] = None


class HealthCheckSummary(BaseModel):
    total_services: int
    healthy: int
    unhealthy: int
    status: str  # "all_healthy" or "degraded"


class FullHealthReport(BaseModel):
    timestamp: datetime
    summary: HealthCheckSummary
    services: Dict[str, ServiceHealthStatus]
