"""Routes package initialization"""
from app.routes.health import router as health_router
from app.routes.scheduler import router as scheduler_router

__all__ = ["health_router", "scheduler_router"]
