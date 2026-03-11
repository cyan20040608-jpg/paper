from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.sentiment import SentimentAnalyzeRequest, SentimentAnalyzeResponse
from backend.app.services.sentiment_service import get_sentiment_service


router = APIRouter(prefix="/api/sentiment", tags=["sentiment"])
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=SentimentAnalyzeResponse)
def analyze_sentiment(payload: SentimentAnalyzeRequest) -> SentimentAnalyzeResponse:
    service = get_sentiment_service()

    if service.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=service.error_message or "妯″瀷灏氭湭灏辩华",
        )

    try:
        return service.analyze(text=payload.text, threshold=payload.threshold)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception(
            "sentiment analyze failed: threshold=%s text_length=%s",
            payload.threshold,
            len(payload.text),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="鎺ㄧ悊澶辫触",
        ) from exc
