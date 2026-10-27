import pytest
from datetime import datetime, timezone
from app.database import SessionLocal, check_db_connection
from app.models.threat import ThreatIndicator, ThreatObservation
from app.services.threat_service import ThreatService


@pytest.fixture(scope="module")
def db_session():
    """Provides a database session for integration tests and cleans up test records."""
    session = SessionLocal()
    yield session
    # Cleanup test records
    session.query(ThreatObservation).filter(ThreatObservation.source_name == "Pytest Integration Test").delete()
    session.query(ThreatIndicator).filter(ThreatIndicator.indicator.like("198.51.100.%")).delete()
    session.commit()
    session.close()


def test_database_connection():
    """Verify live PostgreSQL connectivity."""
    assert check_db_connection() is True


def test_save_indicator_and_deduplication(db_session):
    """
    Verify that ThreatService saves normalized indicators,
    prevents duplicate rows on re-ingestion, and updates timestamps.
    """
    test_indicator = "198.51.100.222"
    item1 = {
        "indicator": test_indicator,
        "indicator_type": "ipv4",
        "category": "suspicious",
        "confidence": 75,
        "country_code": "US",
        "first_seen": datetime(2026, 10, 26, 10, 0, 0, tzinfo=timezone.utc),
        "last_seen": datetime(2026, 10, 26, 10, 0, 0, tzinfo=timezone.utc),
        "source_name": "Pytest Integration Test",
        "source_record_id": "test-pulse-001",
        "source_reference": "https://example.com/pulse/001",
        "description": "Initial test observation",
        "raw_metadata": {"test": True},
    }

    # 1. First ingestion (Insert)
    ind1 = ThreatService.save_indicator(db_session, item1)
    db_session.commit()
    assert ind1.id is not None
    assert ind1.indicator == test_indicator
    assert ind1.category == "suspicious"

    # Verify 1 observation created
    obs_count = db_session.query(ThreatObservation).filter(ThreatObservation.indicator_id == ind1.id).count()
    assert obs_count == 1

    # 2. Second ingestion with upgraded category and newer timestamp (Update)
    item2 = {
        "indicator": test_indicator,
        "indicator_type": "ipv4",
        "category": "c2",  # Upgraded category
        "confidence": 85,
        "country_code": "US",
        "first_seen": datetime(2026, 10, 26, 10, 0, 0, tzinfo=timezone.utc),
        "last_seen": datetime(2026, 10, 27, 8, 0, 0, tzinfo=timezone.utc),  # Newer timestamp
        "source_name": "Pytest Integration Test",
        "source_record_id": "test-pulse-002",
        "source_reference": "https://example.com/pulse/002",
        "description": "Second observation from new campaign",
        "raw_metadata": {"test": True, "campaign": "Cobalt"},
    }

    ind2 = ThreatService.save_indicator(db_session, item2)
    db_session.commit()

    # Same ID (no duplicate indicator row)
    assert ind2.id == ind1.id
    assert ind2.category == "c2"
    assert ind2.last_seen == datetime(2026, 10, 27, 8, 0, 0, tzinfo=timezone.utc)

    # Indicator table count for this IP remains exactly 1
    total_matching = db_session.query(ThreatIndicator).filter(
        ThreatIndicator.indicator == test_indicator,
        ThreatIndicator.indicator_type == "ipv4",
    ).count()
    assert total_matching == 1

    # Observations count increases to 2 (preserving both source attributions)
    obs_count_after = db_session.query(ThreatObservation).filter(ThreatObservation.indicator_id == ind1.id).count()
    assert obs_count_after == 2


def test_get_dashboard_stats(db_session):
    """Verify statistics aggregation reflects real database records."""
    stats = ThreatService.get_dashboard_stats(db_session)
    assert isinstance(stats["total_indicators"], int)
    assert stats["total_indicators"] >= 1
    assert "new_today" in stats
    assert "ip_indicators" in stats
    assert "url_indicators" in stats
    assert stats["last_updated"] is not None


def test_search_exact_indicator(db_session):
    """Verify exact search query finds stored indicator."""
    result = ThreatService.search_exact_indicator(db_session, "198.51.100.222")
    assert result is not None
    assert result.indicator == "198.51.100.222"
    assert result.indicator_type == "ipv4"

    # Search non-existent
    assert ThreatService.search_exact_indicator(db_session, "nonexistent.example.org") is None
