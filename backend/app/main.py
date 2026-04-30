from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import analyze, jobs, media, upload
from app.schemas import HealthResponse


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    get_settings().ensure_dirs()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Crosswalk Watch", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse()

    app.include_router(upload.router)
    app.include_router(jobs.router)
    app.include_router(media.router)
    app.include_router(analyze.router)
    return app


app = create_app()
