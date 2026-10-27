import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from app.config import settings
from app.ingestors.normalizer import normalize_indicator

logger = logging.getLogger(__name__)


class URLhausIngestionError(Exception):
    """Custom exception raised during URLhaus threat intelligence ingestion."""
    pass


class URLhausIngestor:
    """
    Ingestor client for abuse.ch URLhaus.
    Collects malicious URL indicators, normalizes them, and tracks source attribution.
    """

    BASE_URL = "https://urlhaus-api.abuse.ch/v1"

    def __init__(self, api_key: Optional[str] = None, timeout: float = 20.0):
        self.api_key = api_key or settings.URLHAUS_API_KEY
        self.timeout = timeout
        self.client = httpx.Client(
            timeout=self.timeout,
            headers=self._build_headers(),
        )

    def _build_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "ThreatView-Threat-Intelligence/1.0",
        }
        if self.api_key:
            headers["Auth-Key"] = self.api_key
        return headers

    def close(self):
        """Close the underlying HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def fetch_recent_urls(self, limit: int = 50) -> Dict[str, Any]:
        """
        Fetch recently reported malicious URLs from URLhaus.
        Endpoint: /v1/urls/recent/
        """
        if not self.api_key:
            logger.warning(
                "URLhaus Auth-Key not configured. "
                "Free API keys can be generated at the Spamhaus/abuse.ch Customer Portal."
            )

        endpoint = f"{self.BASE_URL}/urls/recent/"

        try:
            response = self.client.get(endpoint)
            
            if response.status_code in (401, 403):
                raise URLhausIngestionError(
                    "URLhaus authentication failed (HTTP 401/403). "
                    "Please configure a valid URLHAUS_API_KEY in backend/.env. "
                    "Keys can be obtained from the abuse.ch / Spamhaus Customer Portal."
                )
            elif response.status_code == 429:
                raise URLhausIngestionError(
                    "URLhaus rate limit exceeded (HTTP 429). Please back off before retrying."
                )

            response.raise_for_status()
            data = response.json()

            query_status = data.get("query_status")
            if query_status in ("unknown_auth_key", "no_auth_key", "unauthorized"):
                raise URLhausIngestionError(
                    f"URLhaus API authentication rejected: '{query_status}'. "
                    "Verify your URLHAUS_API_KEY in backend/.env."
                )

            return data

        except httpx.TimeoutException as exc:
            logger.error(f"URLhaus connection timed out: {exc}")
            raise URLhausIngestionError(f"Connection timed out contacting URLhaus: {exc}")
        except httpx.RequestError as exc:
            logger.error(f"URLhaus network request error: {exc}")
            raise URLhausIngestionError(f"Network error contacting URLhaus: {exc}")

    def parse_record(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transform a single URLhaus JSON record into normalized indicator item(s).
        Extracts both the malicious URL and optionally the host.
        """
        normalized_items: List[Dict[str, Any]] = []
        raw_url = record.get("url")
        if not raw_url:
            return normalized_items

        record_id = str(record.get("id", ""))
        url_ref = record.get("urlhaus_reference") or f"https://urlhaus.abuse.ch/url/{record_id}/"
        threat_type = record.get("threat", "malware_download")
        tags = record.get("tags") or []
        reporter = record.get("reporter", "abuse.ch community")

        # Map threat type and tags to ThreatView category
        category = "malware"
        tag_str = " ".join(tags).lower() if tags else ""
        if "c2" in tag_str or "botnet" in tag_str:
            category = "c2"
        elif "phish" in threat_type.lower() or "phish" in tag_str:
            category = "phishing"
        elif "scanning" in tag_str:
            category = "scanning"

        # Parse timestamp (format: 'YYYY-MM-DD HH:MM:SS UTC')
        first_seen: Optional[datetime] = None
        date_added = record.get("dateadded")
        if date_added:
            try:
                clean_dt = date_added.replace(" UTC", "").strip()
                first_seen = datetime.strptime(clean_dt, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                first_seen = None

        description = f"Malicious URL reported by {reporter} (Status: {record.get('url_status', 'unknown')})"

        # 1. Normalize the primary URL indicator
        try:
            url_indicator = normalize_indicator(
                raw_indicator=raw_url,
                raw_type="url",
                source_name="URLhaus",
                category=category,
                confidence=80,  # High confidence for confirmed URLhaus feed entries
                country_code=None,
                first_seen=first_seen,
                last_seen=first_seen,
                source_reference=url_ref,
                source_record_id=record_id,
                description=description,
                raw_metadata={
                    "urlhaus_id": record_id,
                    "url_status": record.get("url_status"),
                    "threat": threat_type,
                    "tags": tags,
                    "reporter": reporter,
                    "host": record.get("host"),
                },
            )
            normalized_items.append(url_indicator)
        except ValueError as ve:
            logger.debug(f"Skipping malformed URLhaus URL '{raw_url}': {ve}")

        return normalized_items

    def ingest_indicators(self, limit: int = 50) -> Dict[str, Any]:
        """
        Execute full extraction and transformation of URLhaus threat indicators.
        """
        started_at = datetime.now(timezone.utc)
        summary = {
            "source": "URLhaus",
            "started_at": started_at.isoformat(),
            "records_received": 0,
            "indicators_extracted": 0,
            "indicators_normalized": 0,
            "status": "success",
            "indicators": [],
            "error": None,
        }

        try:
            payload = self.fetch_recent_urls(limit=limit)
            raw_urls = payload.get("urls", [])
            summary["records_received"] = len(raw_urls)

            for record in raw_urls:
                items = self.parse_record(record)
                summary["indicators_extracted"] += 1
                summary["indicators"].extend(items)

            summary["indicators_normalized"] = len(summary["indicators"])

        except URLhausIngestionError as err:
            summary["status"] = "failed"
            summary["error"] = str(err)
            logger.error(f"URLhaus ingestion error: {err}")

        return summary
