import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class ThreatIndicator(Base):
    """
    Normalized threat intelligence indicator (IoC).
    Stores canonical representation of IPv4, IPv6, Domain, URL, or File Hash.
    """
    __tablename__ = "threat_indicators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    indicator = Column(Text, nullable=False, index=True)
    indicator_type = Column(String(50), nullable=False, index=True)
    category = Column(String(50), nullable=True, index=True)  # malware, phishing, c2, scanning, suspicious
    confidence = Column(Integer, nullable=True)  # 0 to 100
    country_code = Column(String(2), nullable=True, index=True)  # ISO 3166-1 alpha-2
    first_seen = Column(DateTime(timezone=True), nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    observations = relationship(
        "ThreatObservation",
        back_populates="indicator",
        cascade="all, delete-orphan",
        order_by="desc(ThreatObservation.collected_at)",
    )
    alerts = relationship("Alert", back_populates="indicator", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("indicator", "indicator_type", name="uq_indicator_type"),
        Index("ix_indicators_type_created", "indicator_type", "created_at"),
    )

    def __repr__(self):
        return f"<ThreatIndicator {self.indicator_type}:{self.indicator}>"


class ThreatObservation(Base):
    """
    Source-specific evidence and attribution for a threat indicator.
    Preserves multiple observations of the same indicator across feeds.
    """
    __tablename__ = "threat_observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    indicator_id = Column(
        UUID(as_uuid=True),
        ForeignKey("threat_indicators.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_name = Column(String(100), nullable=False, index=True)  # e.g., 'AlienVault OTX', 'URLhaus'
    source_reference = Column(Text, nullable=True)  # URL to pulse or external report
    source_record_id = Column(String(255), nullable=True)  # ID in the source feed
    description = Column(Text, nullable=True)
    raw_metadata = Column(JSONB().with_variant(JSON(), "sqlite"), nullable=False, default=dict)
    observed_at = Column(DateTime(timezone=True), nullable=True)
    collected_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, index=True)

    # Relationships
    indicator = relationship("ThreatIndicator", back_populates="observations")

    __table_args__ = (
        Index("ix_obs_indicator_source", "indicator_id", "source_name"),
    )

    def __repr__(self):
        return f"<ThreatObservation {self.source_name} -> {self.indicator_id}>"


class IngestionJob(Base):
    """
    Tracks execution metrics, volume, and statuses of scheduled threat feed ingestions.
    """
    __tablename__ = "ingestion_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_name = Column(String(100), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(30), nullable=False, default="running")  # running, completed, failed
    records_received = Column(Integer, nullable=False, default=0)
    records_inserted = Column(Integer, nullable=False, default=0)
    records_updated = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)

    def __repr__(self):
        return f"<IngestionJob {self.source_name} [{self.status}]>"
