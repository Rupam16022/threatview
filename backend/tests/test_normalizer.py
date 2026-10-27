import pytest
from app.ingestors.normalizer import (
    normalize_indicator,
    normalize_ip,
    normalize_domain,
    normalize_url,
    normalize_hash,
)


def test_normalize_valid_ipv4():
    """Verify standard IPv4 address normalization."""
    res = normalize_indicator(
        raw_indicator=" 198.51.100.45 ",
        raw_type="IPv4",
        source_name="AlienVault OTX",
    )
    assert res["indicator"] == "198.51.100.45"
    assert res["indicator_type"] == "ipv4"
    assert res["source_name"] == "AlienVault OTX"


def test_reject_malformed_ipv4():
    """Verify that invalid IPv4 addresses are rejected."""
    with pytest.raises(ValueError, match="Invalid IPv4"):
        normalize_indicator(
            raw_indicator="999.999.999.999",
            raw_type="IPv4",
            source_name="AlienVault OTX",
        )

    with pytest.raises(ValueError, match="Invalid IPv4"):
        normalize_indicator(
            raw_indicator="not-an-ip",
            raw_type="IPv4",
            source_name="AlienVault OTX",
        )


def test_normalize_valid_ipv6():
    """Verify standard IPv6 address normalization."""
    res = normalize_indicator(
        raw_indicator="2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        raw_type="IPv6",
        source_name="AlienVault OTX",
    )
    assert res["indicator_type"] == "ipv6"
    assert res["indicator"] == "2001:db8:85a3::8a2e:370:7334"


def test_normalize_domain_cleaning():
    """Verify domains with protocol prefixes or trailing slashes are cleaned."""
    res = normalize_indicator(
        raw_indicator="https://evil-c2-server.com/ ",
        raw_type="domain",
        source_name="AlienVault OTX",
    )
    assert res["indicator"] == "evil-c2-server.com"
    assert res["indicator_type"] == "domain"


def test_reject_malformed_domain():
    """Verify invalid domain names are rejected."""
    with pytest.raises(ValueError, match="Invalid domain"):
        normalize_domain("evil..com")

    with pytest.raises(ValueError, match="Invalid domain"):
        normalize_domain("invalid_domain_without_tld")


def test_normalize_url():
    """Verify URL normalization standardizes casing and structure."""
    res = normalize_indicator(
        raw_indicator="HTTP://EVIL-DOMAIN.COM:8080/path/to/payload.exe?ref=123",
        raw_type="URL",
        source_name="AlienVault OTX",
    )
    assert res["indicator"] == "http://evil-domain.com:8080/path/to/payload.exe?ref=123"
    assert res["indicator_type"] == "url"


def test_normalize_hashes():
    """Verify SHA256 and MD5 hash normalization."""
    sha256 = "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
    res = normalize_indicator(
        raw_indicator=sha256,
        raw_type="FileHash-SHA256",
        source_name="AlienVault OTX",
    )
    assert res["indicator"] == sha256.lower()
    assert res["indicator_type"] == "hash_sha256"


def test_confidence_and_country_validation():
    """Verify confidence is constrained (0-100) and country code is 2-letter uppercase."""
    res = normalize_indicator(
        raw_indicator="203.0.113.19",
        raw_type="IPv4",
        source_name="AlienVault OTX",
        confidence=85,
        country_code="us",
    )
    assert res["confidence"] == 85
    assert res["country_code"] == "US"

    # Out of bounds confidence should become None
    res_bad_conf = normalize_indicator(
        raw_indicator="203.0.113.19",
        raw_type="IPv4",
        source_name="AlienVault OTX",
        confidence=250,
    )
    assert res_bad_conf["confidence"] is None
