from __future__ import annotations

from fastapi import APIRouter

from backend.app.schemas.sentiment import HealthResponse
from backend.app.services.sentiment_service import get_sentiment_service


router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health_check() -> HealthResponse:
    service = get_sentiment_service()
    return service.health()
