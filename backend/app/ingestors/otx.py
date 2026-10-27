import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import httpx
from app.config import settings
from app.ingestors.normalizer import normalize_indicator

logger = logging.getLogger(__name__)


class OTXIngestionError(Exception):
    """Custom exception raised during AlienVault OTX ingestion."""
    pass


class AlienVaultOTXIngestor:
    """
    Ingestor client for AlienVault Open Threat Exchange (OTX).
    Connects to official OTX endpoints, extracts pulse threat indicators,
    normalizes data, and preserves source attribution.
    """

    BASE_URL = "https://otx.alienvault.com/api/v1"

    def __init__(self, api_key: Optional[str] = None, timeout: float = 20.0):
        self.api_key = api_key or settings.OTX_API_KEY
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
            headers["X-OTX-API-KEY"] = self.api_key
        return headers

    def close(self):
        """Close the underlying HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def fetch_subscribed_pulses(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        Fetch threat intelligence pulses from AlienVault OTX.
        Uses /pulses/subscribed when authenticated, or /pulses/activity.
        """
        if not self.api_key:
            logger.warning(
                "AlienVault OTX API key not configured. "
                "Free API keys can be generated at https://otx.alienvault.com"
            )

        endpoint = f"{self.BASE_URL}/pulses/subscribed"
        params = {"page": page, "limit": limit}

        try:
            response = self.client.get(endpoint, params=params)
            
            if response.status_code == 403 or response.status_code == 401:
                # OTX requires an API key for subscribed pulses
                raise OTXIngestionError(
                    "AlienVault OTX authentication failed (HTTP 403/401). "
                    "Please configure a valid OTX_API_KEY in backend/.env. "
                    "Free keys are available at https://otx.alienvault.com"
                )
            elif response.status_code == 429:
                raise OTXIngestionError(
                    "AlienVault OTX rate limit exceeded (HTTP 429). Please back off before retrying."
                )
            
            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException as exc:
            logger.error(f"AlienVault OTX connection timed out: {exc}")
            raise OTXIngestionError(f"Connection timed out while contacting AlienVault OTX: {exc}")
        except httpx.RequestError as exc:
            logger.error(f"AlienVault OTX request error: {exc}")
            raise OTXIngestionError(f"Network error while contacting AlienVault OTX: {exc}")

    def parse_pulse(self, pulse: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and normalize individual indicators from an OTX pulse record.
        Preserves pulse title, author, and tags for source attribution.
        """
        normalized_indicators: List[Dict[str, Any]] = []
        pulse_id = pulse.get("id")
        pulse_name = pulse.get("name", "Untitled Pulse")
        pulse_author = pulse.get("author_name", "OTX Community")
        pulse_tags = pulse.get("tags", [])
        
        # Determine general category from pulse tags if available
        category = "suspicious"
        if pulse_tags:
            tag_str = " ".join(pulse_tags).lower()
            if any(k in tag_str for k in ["c2", "command and control", "beacon", "botnet"]):
                category = "c2"
            elif any(k in tag_str for k in ["phish", "credential"]):
                category = "phishing"
            elif any(k in tag_str for k in ["ransomware", "trojan", "malware"]):
                category = "malware"
            elif any(k in tag_str for k in ["scanner", "bruteforce"]):
                category = "scanning"

        # Parse pulse creation timestamp
        pulse_created: Optional[datetime] = None
        if pulse.get("created"):
            try:
                pulse_created = datetime.fromisoformat(pulse["created"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pulse_created = None

        raw_indicators = pulse.get("indicators", [])
        for raw_item in raw_indicators:
            raw_val = raw_item.get("indicator")
            raw_type = raw_item.get("type")
            if not raw_val or not raw_type:
                continue

            try:
                normalized = normalize_indicator(
                    raw_indicator=raw_val,
                    raw_type=raw_type,
                    source_name="AlienVault OTX",
                    category=category,
                    confidence=None,  # Do not invent missing confidence
                    country_code=None,
                    first_seen=pulse_created,
                    last_seen=pulse_created,
                    source_reference=f"https://otx.alienvault.com/pulse/{pulse_id}" if pulse_id else None,
                    source_record_id=pulse_id,
                    description=f"Pulse: {pulse_name} (by {pulse_author})",
                    raw_metadata={
                        "pulse_id": pulse_id,
                        "pulse_name": pulse_name,
                        "author": pulse_author,
                        "tags": pulse_tags,
                        "otx_indicator_title": raw_item.get("title"),
                    },
                )
                normalized_indicators.append(normalized)
            except ValueError as ve:
                # Log rejected malformed indicator without crashing
                logger.debug(f"Skipping malformed OTX indicator '{raw_val}' ({raw_type}): {ve}")
                continue

        return normalized_indicators

    def ingest_indicators(self, limit_pulses: int = 5) -> Dict[str, Any]:
        """
        Execute full extraction and transformation of indicators from OTX.
        Returns a summary report with normalized indicator records.
        """
        started_at = datetime.utcnow()
        summary = {
            "source": "AlienVault OTX",
            "started_at": started_at.isoformat(),
            "pulses_processed": 0,
            "indicators_extracted": 0,
            "indicators_normalized": 0,
            "status": "success",
            "indicators": [],
            "error": None,
        }

        try:
            payload = self.fetch_subscribed_pulses(page=1, limit=limit_pulses)
            pulses = payload.get("results", [])
            summary["pulses_processed"] = len(pulses)

            for pulse in pulses:
                items = self.parse_pulse(pulse)
                summary["indicators_extracted"] += len(pulse.get("indicators", []))
                summary["indicators"].extend(items)

            summary["indicators_normalized"] = len(summary["indicators"])

        except OTXIngestionError as err:
            summary["status"] = "failed"
            summary["error"] = str(err)
            logger.error(f"OTX ingestion stopped: {err}")

        return summary
