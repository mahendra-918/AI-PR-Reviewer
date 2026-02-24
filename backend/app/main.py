from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import api_router
from app.core.config import settings
from app.core.logging import setup_logging

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    setup_logging()
    logger.info(
        "app_startup",
        env=settings.app_env,
        llm_model=settings.llm_model,
    )
    yield
    logger.info("app_shutdown")


app = FastAPI(
    title="AI PR Reviewer",
    description=(
        "An open-source, self-hostable AI-powered GitHub Pull Request reviewer. "
        "Combines static analysis (Bandit, Semgrep, ESLint) with LLM-driven code review "
        "using only open-source models (Llama 3, Mixtral, Qwen2.5-Coder)."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
