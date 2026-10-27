import ipaddress
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlparse

# Standard regular expressions for indicator validation
DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z]{2,}$"
)
MD5_REGEX = re.compile(r"^[a-fA-F0-9]{32}$")
SHA1_REGEX = re.compile(r"^[a-fA-F0-9]{40}$")
SHA256_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")

# Map third-party feed indicator types to ThreatView canonical types
TYPE_MAPPING = {
    # AlienVault OTX indicator types
    "ipv4": "ipv4",
    "ipv6": "ipv6",
    "domain": "domain",
    "hostname": "domain",
    "url": "url",
    "uri": "url",
    "filehash-md5": "hash_md5",
    "filehash-sha1": "hash_sha1",
    "filehash-sha256": "hash_sha256",
    "cve": "cve",
    # Generic fallbacks
    "ip": "ipv4",
    "hash": "hash_sha256",
}


def normalize_indicator_type(raw_type: str) -> str:
    """Normalize raw indicator type to canonical ThreatView indicator_type."""
    if not raw_type:
        return "unknown"
    clean_type = raw_type.strip().lower()
    return TYPE_MAPPING.get(clean_type, clean_type)


def normalize_ip(value: str) -> str:
    """Validate and return normalized IPv4 or IPv6 address string."""
    value = value.strip()
    # ipaddress handles parsing and standard string representation
    ip_obj = ipaddress.ip_address(value)
    return str(ip_obj)


def normalize_domain(value: str) -> str:
    """Validate and return normalized domain name."""
    value = value.strip().lower()
    # Strip protocol if accidentally included in domain field
    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        value = parsed.netloc or parsed.path
    # Strip port if present
    if ":" in value:
        value = value.split(":")[0]
    # Strip trailing slash or dot
    value = value.rstrip("/.")
    
    if not DOMAIN_REGEX.match(value):
        raise ValueError(f"Invalid domain format: '{value}'")
    return value


def normalize_url(value: str) -> str:
    """Validate and return normalized URL."""
    value = value.strip()
    if not value.lower().startswith(("http://", "https://")):
        value = f"http://{value}"
    
    parsed = urlparse(value)
    if not parsed.netloc:
        raise ValueError(f"Invalid URL missing network location: '{value}'")

    host = parsed.hostname or (parsed.netloc.split(":")[0] if parsed.netloc else "")
    if not host:
        raise ValueError(f"Invalid URL missing host: '{value}'")

    # Host must either be a valid IP address or have valid domain structure
    try:
        ipaddress.ip_address(host)
    except ValueError:
        if "." not in host:
            raise ValueError(f"Invalid URL host '{host}' (no domain suffix or IP format)")
    
    # Normalize scheme and host to lowercase, keep path and query intact
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    query = f"?{parsed.query}" if parsed.query else ""
    fragment = f"#{parsed.fragment}" if parsed.fragment else ""
    
    return f"{scheme}://{netloc}{path}{query}{fragment}"


def normalize_hash(value: str, hash_type: str) -> str:
    """Validate and return normalized lowercase hash."""
    value = value.strip().lower()
    if hash_type == "hash_md5" and not MD5_REGEX.match(value):
        raise ValueError(f"Invalid MD5 hash format: '{value}'")
    elif hash_type == "hash_sha1" and not SHA1_REGEX.match(value):
        raise ValueError(f"Invalid SHA1 hash format: '{value}'")
    elif hash_type == "hash_sha256" and not SHA256_REGEX.match(value):
        raise ValueError(f"Invalid SHA256 hash format: '{value}'")
    return value


def normalize_indicator(
    raw_indicator: str,
    raw_type: str,
    source_name: str,
    category: Optional[str] = None,
    confidence: Optional[int] = None,
    country_code: Optional[str] = None,
    first_seen: Optional[datetime] = None,
    last_seen: Optional[datetime] = None,
    source_reference: Optional[str] = None,
    source_record_id: Optional[str] = None,
    description: Optional[str] = None,
    raw_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Core ETL Normalizer function.
    Transforms raw indicator data from external feeds into the ThreatView unified schema.
    Raises ValueError on invalid/malformed indicators.
    """
    if not raw_indicator or not isinstance(raw_indicator, str):
        raise ValueError("Indicator value must be a non-empty string.")

    cleaned_indicator = raw_indicator.strip()
    indicator_type = normalize_indicator_type(raw_type)

    # Perform strict type-specific validation and normalization
    if indicator_type == "ipv4":
        try:
            ip_obj = ipaddress.IPv4Address(cleaned_indicator)
            normalized_value = str(ip_obj)
        except ipaddress.AddressValueError:
            raise ValueError(f"Invalid IPv4 indicator: '{cleaned_indicator}'")
    elif indicator_type == "ipv6":
        try:
            ip_obj = ipaddress.IPv6Address(cleaned_indicator)
            normalized_value = str(ip_obj)
        except ipaddress.AddressValueError:
            raise ValueError(f"Invalid IPv6 indicator: '{cleaned_indicator}'")
    elif indicator_type in ("domain", "hostname"):
        normalized_value = normalize_domain(cleaned_indicator)
        indicator_type = "domain"
    elif indicator_type == "url":
        normalized_value = normalize_url(cleaned_indicator)
    elif indicator_type.startswith("hash_"):
        normalized_value = normalize_hash(cleaned_indicator, indicator_type)
    else:
        # Generic fallback without transformation
        normalized_value = cleaned_indicator

    # Validate confidence range (0-100) if provided
    valid_confidence: Optional[int] = None
    if confidence is not None:
        try:
            conf_int = int(confidence)
            if 0 <= conf_int <= 100:
                valid_confidence = conf_int
        except (ValueError, TypeError):
            valid_confidence = None

    # Normalize 2-letter country code if present
    valid_country: Optional[str] = None
    if country_code and isinstance(country_code, str):
        c_code = country_code.strip().upper()
        if len(c_code) == 2 and c_code.isalpha():
            valid_country = c_code

    # UTC collection timestamp
    collected_at = datetime.now(timezone.utc)

    return {
        "indicator": normalized_value,
        "indicator_type": indicator_type,
        "category": category.strip().lower() if category else "suspicious",
        "confidence": valid_confidence,
        "country_code": valid_country,
        "first_seen": first_seen,
        "last_seen": last_seen or first_seen,
        "collected_at": collected_at,
        # Evidence & Attribution fields (Section 8: threat_observations)
        "source_name": source_name,
        "source_reference": source_reference,
        "source_record_id": str(source_record_id) if source_record_id else None,
        "description": description,
        "raw_metadata": raw_metadata or {},
    }
