import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class MonitoredDomain(Base):
    """
    Domains registered by authenticated users for automated threat detection.
    """
    __tablename__ = "monitored_domains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    domain = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    user = relationship("User", back_populates="monitored_domains")

    __table_args__ = (
        Index("ix_monitored_domain_user", "domain", "user_id"),
    )

    def __repr__(self):
        return f"<MonitoredDomain {self.domain} (Active: {self.is_active})>"


class Alert(Base):
    """
    Security alert generated when an ingested indicator matches a monitored domain.
    """
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    indicator_id = Column(
        UUID(as_uuid=True),
        ForeignKey("threat_indicators.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    alert_type = Column(String(50), nullable=False, default="domain_match")
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, index=True)
    email_sent = Column(Boolean, nullable=False, default=False)
    read_status = Column(Boolean, nullable=False, default=False)

    # Relationships
    user = relationship("User", back_populates="alerts")
    indicator = relationship("ThreatIndicator", back_populates="alerts")

    def __repr__(self):
        return f"<Alert {self.alert_type} -> User:{self.user_id}>"
