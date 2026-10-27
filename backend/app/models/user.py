import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    """
    ThreatView User account model supporting Free and Pro tier access.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    organization_name = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    subscription_plan = Column(String(50), nullable=False, default="free")  # 'free' or 'pro'
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    # Relationships
    monitored_domains = relationship(
        "MonitoredDomain",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    alerts = relationship(
        "Alert",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User {self.email} ({self.subscription_plan})>"
