from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.threat import (
    DashboardStatsOut,
    TrendItemOut,
    CategoryItemOut,
    CountryItemOut,
    SourceItemOut,
)
from app.services.threat_service import ThreatService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsOut)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Return overall dashboard statistics computed from live DB data."""
    stats = ThreatService.get_dashboard_stats(db)
    return stats


@router.get("/trends", response_model=List[TrendItemOut])
def get_trends(days: int = 30, db: Session = Depends(get_db)):
    """Return daily new-indicator counts for the past ``days`` days (default 30)."""
    return ThreatService.get_trends(db, days)


@router.get("/categories", response_model=List[CategoryItemOut])
def get_categories(db: Session = Depends(get_db)):
    """Return distribution of indicators grouped by threat category."""
    return ThreatService.get_category_distribution(db)


@router.get("/countries", response_model=List[CountryItemOut])
def get_countries(db: Session = Depends(get_db)):
    """Return distribution of indicators grouped by country code."""
    return ThreatService.get_country_distribution(db)


@router.get("/sources", response_model=List[SourceItemOut])
def get_sources(db: Session = Depends(get_db)):
    """Return distribution of indicators grouped by source feed name."""
    return ThreatService.get_source_distribution(db)
