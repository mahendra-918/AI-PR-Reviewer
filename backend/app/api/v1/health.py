from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health", summary="Health Check", tags=["infra"])
async def health_check() -> JSONResponse:
    """Returns service health status."""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "ai-pr-reviewer",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
