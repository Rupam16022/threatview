import pytest
import httpx
from app.ingestors.otx import AlienVaultOTXIngestor, OTXIngestionError

# Sample real-world structured OTX pulse payload for testing
MOCK_PULSE_RESPONSE = {
    "count": 1,
    "results": [
        {
            "id": "66f1234567890abcdef12345",
            "name": "Cobalt Strike C2 Infrastructure Observed",
            "description": "Indicators associated with active Cobalt Strike beacon communications.",
            "author_name": "ThreatHunter_Sec",
            "created": "2026-10-26T14:30:00Z",
            "tags": ["cobalt strike", "c2", "malware", "apt"],
            "indicators": [
                {
                    "id": 101,
                    "indicator": "198.51.100.99",
                    "type": "IPv4",
                    "title": "C2 Server Node",
                },
                {
                    "id": 102,
                    "indicator": "http://malicious-beacon.example.com/api/v1/ping",
                    "type": "URL",
                    "title": "Staging Beacon URL",
                },
                {
                    "id": 103,
                    "indicator": "malicious-beacon.example.com",
                    "type": "domain",
                    "title": "C2 Domain",
                },
                {
                    "id": 104,
                    "indicator": "invalid-ip-999.999.999.999",
                    "type": "IPv4",
                    "title": "Corrupt Indicator in Feed",
                },
            ],
        }
    ],
}


def test_parse_pulse_indicators():
    """Verify indicators are accurately extracted and normalized from pulse records."""
    ingestor = AlienVaultOTXIngestor(api_key="test_dummy_key")
    pulse = MOCK_PULSE_RESPONSE["results"][0]
    indicators = ingestor.parse_pulse(pulse)

    # 4 indicators in pulse, but 1 is corrupt (999.999.999.999) -> expect 3 valid
    assert len(indicators) == 3

    # Check IPv4 extraction
    ip_ind = next(item for item in indicators if item["indicator_type"] == "ipv4")
    assert ip_ind["indicator"] == "198.51.100.99"
    assert ip_ind["category"] == "c2"  # Inferred from pulse tags
    assert ip_ind["source_name"] == "AlienVault OTX"
    assert ip_ind["source_record_id"] == "66f1234567890abcdef12345"
    assert "https://otx.alienvault.com/pulse/66f1234567890abcdef12345" in ip_ind["source_reference"]

    # Check URL extraction
    url_ind = next(item for item in indicators if item["indicator_type"] == "url")
    assert url_ind["indicator"] == "http://malicious-beacon.example.com/api/v1/ping"

    # Check Domain extraction
    dom_ind = next(item for item in indicators if item["indicator_type"] == "domain")
    assert dom_ind["indicator"] == "malicious-beacon.example.com"


def test_otx_authentication_error_handling(monkeypatch):
    """Verify that HTTP 403 / 401 returns an informative, non-crashing OTXIngestionError."""
    ingestor = AlienVaultOTXIngestor(api_key="")

    # Mock client.get returning 403
    def mock_get(*args, **kwargs):
        req = httpx.Request("GET", "https://otx.alienvault.com/api/v1/pulses/subscribed")
        return httpx.Response(403, request=req, json={"detail": "Authentication required"})

    monkeypatch.setattr(ingestor.client, "get", mock_get)

    with pytest.raises(OTXIngestionError, match="AlienVault OTX authentication failed"):
        ingestor.fetch_subscribed_pulses()


def test_otx_rate_limit_error_handling(monkeypatch):
    """Verify that HTTP 429 raises rate limit exception."""
    ingestor = AlienVaultOTXIngestor(api_key="test_key")

    def mock_get(*args, **kwargs):
        req = httpx.Request("GET", "https://otx.alienvault.com/api/v1/pulses/subscribed")
        return httpx.Response(429, request=req)

    monkeypatch.setattr(ingestor.client, "get", mock_get)

    with pytest.raises(OTXIngestionError, match="rate limit exceeded"):
        ingestor.fetch_subscribed_pulses()
