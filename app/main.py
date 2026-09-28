from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.webhook import router as webhook_router
from app.utils.config import settings
from app.utils.logger import configure_logging, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    logger.info(
        "application_starting",
        environment=settings.environment,
        version=settings.app_version,
    )

    yield

    logger.info("application_stopping")


app = FastAPI(
    title=settings.app_name,
    description=(
        "Conversational commerce and end-to-end "
        "sales agent for Zoey Bambini"
    ),
    version=settings.app_version,
    lifespan=lifespan,
)


app.include_router(health_router)
app.include_router(webhook_router)


@app.get("/")
async def root():
    return {
        "service": settings.app_name,
        "status": "running",
        "version": settings.app_version,
    }
