from __future__ import annotations

import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse

from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.sentiment import router as sentiment_router
from backend.app.core.settings import settings
from backend.app.services.sentiment_service import get_sentiment_service


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

FRONTEND_DIST_DIR = settings.project_root / "frontend" / "dist"
FRONTEND_INDEX_FILE = FRONTEND_DIST_DIR / "index.html"
FRONTEND_ASSETS_DIR = FRONTEND_DIST_DIR / "assets"


@asynccontextmanager
async def lifespan(_: FastAPI):
    service = get_sentiment_service()

    def _helper_preload_model() -> None:
        try:
            service.load()
        except Exception:
            logger.exception("模型后台加载失败")

    loader_thread = threading.Thread(
        target=_helper_preload_model,
        name="sentiment-model-loader",
        daemon=True,
    )
    loader_thread.start()
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
app.add_middleware(GZipMiddleware, minimum_size=1024)

app.include_router(health_router)
app.include_router(sentiment_router)


@app.get("/assets/{asset_path:path}", include_in_schema=False)
def serve_frontend_asset(asset_path: str) -> FileResponse:
    if not FRONTEND_ASSETS_DIR.exists():
        raise HTTPException(
            status_code=503,
            detail="前端静态资源不存在，请先在 frontend 目录执行 npm run build",
        )

    asset_file = (FRONTEND_ASSETS_DIR / asset_path).resolve()
    assets_root = FRONTEND_ASSETS_DIR.resolve()

    if assets_root not in asset_file.parents or not asset_file.is_file():
        raise HTTPException(status_code=404, detail="Not Found")

    return FileResponse(
        asset_file,
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",
        },
    )


@app.get("/", include_in_schema=False)
@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str = "") -> FileResponse:
    if full_path == "api" or full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")

    if not FRONTEND_DIST_DIR.exists() or not FRONTEND_INDEX_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail="前端静态资源不存在，请先在 frontend 目录执行 npm run build",
        )

    requested_path = (FRONTEND_DIST_DIR / full_path).resolve()
    dist_root = FRONTEND_DIST_DIR.resolve()

    if dist_root not in requested_path.parents and requested_path != dist_root:
        raise HTTPException(status_code=404, detail="Not Found")

    if full_path and requested_path.is_file():
        return FileResponse(
            requested_path,
            headers={
                "Cache-Control": "public, max-age=3600",
            },
        )

    return FileResponse(
        FRONTEND_INDEX_FILE,
        headers={
            "Cache-Control": "no-cache",
        },
    )
