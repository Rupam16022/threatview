import pytest
import httpx
from datetime import datetime, timezone
from app.database import SessionLocal
from app.models.threat import ThreatIndicator, ThreatObservation, IngestionJob
from app.services.threat_service import ThreatService
from app.ingestors.urlhaus import URLhausIngestor, URLhausIngestionError

# Sample real-world structured URLhaus response payload
MOCK_URLHAUS_RESPONSE = {
    "query_status": "ok",
    "urls": [
        {
            "id": "3391821",
            "urlhaus_reference": "https://urlhaus.abuse.ch/url/3391821/",
            "url": "http://198.51.100.80:8080/bins/mirai.arm7",
            "url_status": "online",
            "host": "198.51.100.80",
            "dateadded": "2026-10-27 02:15:00 UTC",
            "threat": "malware_download",
            "reporter": "security_researcher_alpha",
            "tags": ["mirai", "botnet", "elf"],
        },
        {
            "id": "3391822",
            "urlhaus_reference": "https://urlhaus.abuse.ch/url/3391822/",
            "url": "https://compromised-site.org/wp-content/phish.html",
            "url_status": "offline",
            "host": "compromised-site.org",
            "dateadded": "2026-10-27 03:00:00 UTC",
            "threat": "phishing",
            "reporter": "phish_hunter_beta",
            "tags": ["credential_harvesting"],
        },
        {
            "id": "3391823",
            "urlhaus_reference": "https://urlhaus.abuse.ch/url/3391823/",
            "url": "not-a-valid-url-without-host",
            "url_status": "unknown",
            "threat": "malware",
            "tags": [],
        },
    ],
}


def test_parse_urlhaus_records():
    """Verify URLhaus records are parsed and categorized correctly."""
    ingestor = URLhausIngestor(api_key="test_key")
    records = MOCK_URLHAUS_RESPONSE["urls"]

    # 3 records, but 3rd has invalid URL -> expect 2 normalized
    parsed = []
    for r in records:
        parsed.extend(ingestor.parse_record(r))

    assert len(parsed) == 2

    # Verify first item (botnet / malware)
    item1 = parsed[0]
    assert item1["indicator"] == "http://198.51.100.80:8080/bins/mirai.arm7"
    assert item1["indicator_type"] == "url"
    assert item1["category"] == "c2"  # Inferred from 'botnet' tag
    assert item1["source_name"] == "URLhaus"
    assert item1["source_record_id"] == "3391821"
    assert "https://urlhaus.abuse.ch/url/3391821/" in item1["source_reference"]
    assert item1["first_seen"] == datetime(2026, 10, 27, 2, 15, 0, tzinfo=timezone.utc)

    # Verify second item (phishing)
    item2 = parsed[1]
    assert item2["indicator"] == "https://compromised-site.org/wp-content/phish.html"
    assert item2["category"] == "phishing"


def test_urlhaus_auth_failure_handling(monkeypatch):
    """Verify that HTTP 401/403 or unknown_auth_key raises URLhausIngestionError."""
    ingestor = URLhausIngestor(api_key="invalid_key")

    def mock_get(*args, **kwargs):
        req = httpx.Request("GET", "https://urlhaus-api.abuse.ch/v1/urls/recent/")
        return httpx.Response(403, request=req, json={"query_status": "unknown_auth_key"})

    monkeypatch.setattr(ingestor.client, "get", mock_get)

    with pytest.raises(URLhausIngestionError, match="URLhaus authentication failed"):
        ingestor.fetch_recent_urls()


def test_multi_feed_deduplication_and_attribution():
    """
    Deliverable: Two feeds feeding one database.
    Verify that when Feed 1 (OTX) and Feed 2 (URLhaus) observe the SAME URL,
    only 1 unique threat_indicator row exists, while 2 distinct observations are preserved.
    """
    db = SessionLocal()
    shared_url = "http://shared-threat-payload.example.org/loader.sh"

    # Cleanup any prior test run
    db.query(ThreatObservation).filter(ThreatObservation.source_name.in_(["AlienVault OTX", "URLhaus"])).delete()
    db.query(ThreatIndicator).filter(ThreatIndicator.indicator == shared_url).delete()
    db.commit()

    try:
        # Feed 1: AlienVault OTX observes the URL
        otx_indicator = {
            "indicator": shared_url,
            "indicator_type": "url",
            "category": "suspicious",
            "confidence": 60,
            "country_code": None,
            "first_seen": datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc),
            "last_seen": datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc),
            "source_name": "AlienVault OTX",
            "source_record_id": "pulse-otx-shared-99",
            "source_reference": "https://otx.alienvault.com/pulse/pulse-otx-shared-99",
            "description": "Observed in OTX APT Pulse",
            "raw_metadata": {"otx_tag": "trojan"},
        }
        ThreatService.save_indicator(db, otx_indicator)
        db.commit()

        # Check: 1 indicator, 1 observation
        ind_row = db.query(ThreatIndicator).filter(ThreatIndicator.indicator == shared_url).first()
        assert ind_row is not None
        assert ind_row.category == "suspicious"
        assert len(ind_row.observations) == 1
        assert ind_row.observations[0].source_name == "AlienVault OTX"

        # Feed 2: URLhaus observes the EXACT SAME URL, but with upgraded category 'malware'
        urlhaus_indicator = {
            "indicator": shared_url,
            "indicator_type": "url",
            "category": "malware",
            "confidence": 85,
            "country_code": None,
            "first_seen": datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc),
            "last_seen": datetime(2026, 10, 27, 4, 0, 0, tzinfo=timezone.utc),  # newer
            "source_name": "URLhaus",
            "source_record_id": "urlhaus-id-8831",
            "source_reference": "https://urlhaus.abuse.ch/url/urlhaus-id-8831/",
            "description": "Active malware drop site reported on URLhaus",
            "raw_metadata": {"urlhaus_status": "online"},
        }
        ThreatService.save_indicator(db, urlhaus_indicator)
        db.commit()

        # Check after second feed:
        # Still exactly ONE row in threat_indicators
        matching_count = db.query(ThreatIndicator).filter(ThreatIndicator.indicator == shared_url).count()
        assert matching_count == 1

        # Check updated properties
        updated_ind = db.query(ThreatIndicator).filter(ThreatIndicator.indicator == shared_url).first()
        assert updated_ind.category == "malware"  # Upgraded category
        assert updated_ind.last_seen == datetime(2026, 10, 27, 4, 0, 0, tzinfo=timezone.utc)

        # Observations count must now be TWO (both feeds preserved!)
        observations = db.query(ThreatObservation).filter(ThreatObservation.indicator_id == updated_ind.id).all()
        assert len(observations) == 2
        sources = {obs.source_name for obs in observations}
        assert "AlienVault OTX" in sources
        assert "URLhaus" in sources

    finally:
        # Cleanup
        db.query(ThreatObservation).filter(ThreatObservation.source_name.in_(["AlienVault OTX", "URLhaus"])).delete()
        db.query(ThreatIndicator).filter(ThreatIndicator.indicator == shared_url).delete()
        db.commit()
        db.close()
