from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.sentiment import router as sentiment_router
from backend.app.core.settings import settings
from backend.app.services.sentiment_service import get_sentiment_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    service = get_sentiment_service()
    try:
        service.load()
    except Exception as exc:
        print(f"模型预加载失败: {exc}")
    yield


app = FastAPI(
    title="校园论坛情感分析服务",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(sentiment_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "sentiment-service-ready"}
