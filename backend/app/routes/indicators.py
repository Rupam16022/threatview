from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.threat import IndicatorOut
from app.services.threat_service import ThreatService

router = APIRouter(prefix="/indicators", tags=["Indicators"])


@router.get("", response_model=List[IndicatorOut])
def list_indicators(
    limit: int = Query(25, ge=1, le=200),
    offset: int = Query(0, ge=0),
    indicator_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Paginated list of threat indicators with optional filtering by type or category.
    """
    return ThreatService.get_recent_indicators(
        db,
        limit=limit,
        offset=offset,
        indicator_type=indicator_type,
        category=category,
    )


@router.get("/search", response_model=IndicatorOut)
def search_indicator(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    """
    Exact-match lookup for an IoC (IP, domain, URL, or hash).
    Returns 404 if the indicator is not in the threat database.
    """
    result = ThreatService.search_exact_indicator(db, q)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Indicator '{q}' not found in threat database.",
        )
    return result


@router.get("/{indicator_id}", response_model=IndicatorOut)
def get_indicator(indicator_id: UUID, db: Session = Depends(get_db)):
    """Fetch a single threat indicator by its UUID, including all source observations."""
    indicator = ThreatService.get_indicator_by_id(db, indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found.")
    return indicator
