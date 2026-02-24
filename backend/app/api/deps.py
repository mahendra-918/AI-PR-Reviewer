from fastapi import APIRouter

from app.api.v1 import health, webhook

api_router = APIRouter()

api_router.include_router(health.router, prefix="/api/v1")
api_router.include_router(webhook.router, prefix="/api/v1")
