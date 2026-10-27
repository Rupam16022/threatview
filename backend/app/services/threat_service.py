import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_

from app.models.threat import ThreatIndicator, ThreatObservation, IngestionJob

logger = logging.getLogger(__name__)


class ThreatService:
    """
    Core persistence and query service for cybersecurity threat intelligence.
    Handles deduplication, observation tracking, and statistical aggregations.
    """

    @staticmethod
    def save_indicator(db: Session, item: Dict[str, Any]) -> ThreatIndicator:
        """
        Store or update a normalized threat indicator and record its observation.
        Prevents duplicate indicator rows while preserving individual source observations.
        """
        indicator_val = item["indicator"]
        ind_type = item["indicator_type"]

        # 1. Check for existing indicator (composite match on indicator + indicator_type)
        existing = (
            db.query(ThreatIndicator)
            .filter(
                ThreatIndicator.indicator == indicator_val,
                ThreatIndicator.indicator_type == ind_type,
            )
            .first()
        )

        now = datetime.now(timezone.utc)

        if existing:
            # Update timestamps and enrich metadata if missing
            if item.get("last_seen"):
                if not existing.last_seen or item["last_seen"] > existing.last_seen:
                    existing.last_seen = item["last_seen"]
            existing.updated_at = now

            # If existing is generic 'suspicious' and incoming is specific, upgrade category
            if existing.category == "suspicious" and item.get("category") and item["category"] != "suspicious":
                existing.category = item["category"]

            if not existing.country_code and item.get("country_code"):
                existing.country_code = item["country_code"]

            indicator_record = existing
        else:
            # Insert new indicator
            indicator_record = ThreatIndicator(
                indicator=indicator_val,
                indicator_type=ind_type,
                category=item.get("category", "suspicious"),
                confidence=item.get("confidence"),
                country_code=item.get("country_code"),
                first_seen=item.get("first_seen") or now,
                last_seen=item.get("last_seen") or now,
                created_at=now,
                updated_at=now,
            )
            db.add(indicator_record)
            db.flush()  # Flush to generate indicator_record.id for foreign key

        # 2. Record source observation (attribution)
        source_name = item.get("source_name", "Unknown Feed")
        source_record_id = item.get("source_record_id")

        # Check for existing observation to prevent duplicate observation spam
        obs_query = db.query(ThreatObservation).filter(
            ThreatObservation.indicator_id == indicator_record.id,
            ThreatObservation.source_name == source_name,
        )
        if source_record_id:
            obs_query = obs_query.filter(ThreatObservation.source_record_id == source_record_id)

        existing_obs = obs_query.first()
        if not existing_obs:
            observation = ThreatObservation(
                indicator_id=indicator_record.id,
                source_name=source_name,
                source_reference=item.get("source_reference"),
                source_record_id=source_record_id,
                description=item.get("description"),
                raw_metadata=item.get("raw_metadata") or {},
                observed_at=item.get("first_seen") or now,
                collected_at=now,
            )
            db.add(observation)

        return indicator_record

    @classmethod
    def save_batch(cls, db: Session, indicators: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Store a collection of normalized indicators in a single database transaction.
        """
        inserted_count = 0
        updated_count = 0

        for item in indicators:
            indicator_val = item["indicator"]
            ind_type = item["indicator_type"]

            exists = (
                db.query(ThreatIndicator.id)
                .filter(
                    ThreatIndicator.indicator == indicator_val,
                    ThreatIndicator.indicator_type == ind_type,
                )
                .first()
            )

            cls.save_indicator(db, item)
            if exists:
                updated_count += 1
            else:
                inserted_count += 1

        db.commit()
        return {"inserted": inserted_count, "updated": updated_count}

    @staticmethod
    def get_recent_indicators(
        db: Session,
        limit: int = 50,
        offset: int = 0,
        indicator_type: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[ThreatIndicator]:
        """Fetch recently observed threat indicators with pagination."""
        query = db.query(ThreatIndicator)
        if indicator_type:
            query = query.filter(ThreatIndicator.indicator_type == indicator_type.lower())
        if category:
            query = query.filter(ThreatIndicator.category == category.lower())

        return (
            query.order_by(desc(ThreatIndicator.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_indicator_by_id(db: Session, indicator_id: UUID) -> Optional[ThreatIndicator]:
        """Fetch threat indicator details including source observations."""
        return db.query(ThreatIndicator).filter(ThreatIndicator.id == indicator_id).first()

    @staticmethod
    def search_exact_indicator(db: Session, query_str: str) -> Optional[ThreatIndicator]:
        """Search for an exact indicator match (IP, domain, URL, or hash)."""
        clean_q = query_str.strip().lower()
        return (
            db.query(ThreatIndicator)
            .filter(func.lower(ThreatIndicator.indicator) == clean_q)
            .first()
        )

    @staticmethod
    def get_dashboard_stats(db: Session) -> Dict[str, Any]:
        """
        Compute real statistics directly from the threat intelligence tables.
        Never returns fabricated numbers.
        """
        total = db.query(func.count(ThreatIndicator.id)).scalar() or 0
        
        # New indicators in the last 24 hours
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        new_today = (
            db.query(func.count(ThreatIndicator.id))
            .filter(ThreatIndicator.created_at >= cutoff)
            .scalar()
            or 0
        )

        ip_indicators = (
            db.query(func.count(ThreatIndicator.id))
            .filter(ThreatIndicator.indicator_type.in_(["ipv4", "ipv6"]))
            .scalar()
            or 0
        )

        url_indicators = (
            db.query(func.count(ThreatIndicator.id))
            .filter(ThreatIndicator.indicator_type == "url")
            .scalar()
            or 0
        )

        latest_rec = (
            db.query(ThreatIndicator.created_at)
            .order_by(desc(ThreatIndicator.created_at))
            .first()
        )
        last_updated = latest_rec[0].isoformat() if latest_rec else None

        return {
            "total_indicators": total,
            "new_today": new_today,
            "ip_indicators": ip_indicators,
            "url_indicators": url_indicators,
            "last_updated": last_updated,
        }
