"""Routes package initialization"""
from app.routes.health import router as health_router
from app.routes.scheduler import router as scheduler_router
from app.routes.dashboard import router as dashboard_router
from app.routes.indicators import router as indicators_router
from app.routes.monitoring import router as monitoring_router
from app.routes.reports import router as reports_router

__all__ = [
    "health_router",
    "scheduler_router",
    "dashboard_router",
    "indicators_router",
    "monitoring_router",
    "reports_router",
]
