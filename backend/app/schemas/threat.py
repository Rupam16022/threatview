from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ObservationOut(BaseModel):
    id: UUID
    source_name: str
    source_reference: Optional[str] = None
    source_record_id: Optional[str] = None
    description: Optional[str] = None
    raw_metadata: Dict[str, Any] = {}
    observed_at: Optional[datetime] = None
    collected_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IndicatorOut(BaseModel):
    id: UUID
    indicator: str
    indicator_type: str
    category: Optional[str] = None
    confidence: Optional[int] = None
    country_code: Optional[str] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    observations: List[ObservationOut] = []

    model_config = ConfigDict(from_attributes=True)


class DashboardStatsOut(BaseModel):
    total_indicators: int
    new_today: int
    ip_indicators: int
    url_indicators: int
    last_updated: Optional[str] = None


class TrendItemOut(BaseModel):
    date: str  # YYYY-MM-DD
    count: int


class CategoryItemOut(BaseModel):
    category: str
    count: int


class CountryItemOut(BaseModel):
    country_code: str
    count: int


class SourceItemOut(BaseModel):
    source_name: str
    count: int
