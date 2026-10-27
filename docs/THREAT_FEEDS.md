# Threat Intelligence Feeds Documentation

ThreatView ingests and normalizes indicators of compromise (IoCs) exclusively from reputable open-source threat intelligence (OSINT) providers. This document outlines the technical specification, rate limits, and attribution requirements for each feed.

---

## 1. AlienVault Open Threat Exchange (OTX)

- **Source Name:** AlienVault OTX (AT&T Cybersecurity)
- **Official Website:** [https://otx.alienvault.com/](https://otx.alienvault.com/)
- **Documentation:** [https://otx.alienvault.com/api](https://otx.alienvault.com/api)
- **Status:** **Integrated (Day 2)**

### Endpoints Used
1. `GET /api/v1/pulses/subscribed`
   - Purpose: Fetches threat pulses published by security researchers and organizations followed by the user.
   - Query Parameters: `page` (int), `limit` (int, default: 20)
2. `GET /api/v1/pulses/activity`
   - Purpose: Global activity stream of public pulses.

### Authentication Requirements
- **Header:** `X-OTX-API-KEY: <API_KEY>`
- **Cost:** 100% Free. Users can sign up at `https://otx.alienvault.com` and obtain their personal API key from their account profile settings.
- **Environment Variable:** `OTX_API_KEY` in `backend/.env`.

### Refresh Frequency
- **Default Ingestion Interval:** Every 60 minutes via background scheduler (APScheduler).
- **Manual Trigger:** `python -m app.ingestors.run --source otx --limit 5`

### Collected Data Fields
| Raw OTX Field | ThreatView Schema Field | Transformation / Normalization |
|---|---|---|
| `indicator.indicator` | `indicator` | Stripped, validated according to type (IPv4, IPv6, Domain, URL, Hash) |
| `indicator.type` | `indicator_type` | Mapped to canonical type (`ipv4`, `ipv6`, `domain`, `url`, `hash_sha256`, etc.) |
| `pulse.tags` | `category` | Mapped to `malware`, `phishing`, `c2`, `scanning`, or `suspicious` |
| `pulse.created` | `first_seen`, `last_seen` | Converted to timezone-aware UTC ISO timestamp |
| `pulse.id` | `source_record_id` | Preserved for traceability and pulse linking |
| `pulse.name` / `author` | `description` | e.g. `"Pulse: Lazarus APT (by AlienVault)"` |

### Rate Limits & Headers
- Default rate limit: Approximately 1,000 requests per hour per account.
- Rate limit response: HTTP 429 Too Many Requests.
- The ingestor implements backoff and non-crashing exception handling.

### Known Limitations
- Not every indicator in a public pulse includes geolocation (`country_code`) or quantitative severity/confidence scores.
- In accordance with the project specification: *unknown values remain null and are never fabricated*.

### Attribution Requirements
- Indicator records retain explicit attribution to `AlienVault OTX` and link directly to the source pulse: `https://otx.alienvault.com/pulse/{pulse_id}`.

---

## 2. URLhaus (abuse.ch)

- **Source Name:** URLhaus (abuse.ch & Spamhaus)
- **Official Website:** [https://urlhaus.abuse.ch/](https://urlhaus.abuse.ch/)
- **API Documentation:** [https://urlhaus-api.abuse.ch/](https://urlhaus-api.abuse.ch/)
- **Status:** **Integrated (Day 4)**

### Endpoints Used
1. `GET /v1/urls/recent/`
   - Purpose: Fetches the most recently submitted malicious URLs actively distributing malware or associated with botnet payloads.
   - Response: JSON payload containing list of records with `id`, `url`, `url_status`, `threat`, `tags`, `reporter`, `dateadded`, `urlhaus_reference`.

### Authentication Requirements
- **Header:** `Auth-Key: <URLHAUS_API_KEY>`
- **Cost:** Free community access available via the Spamhaus / abuse.ch Customer Portal.
- **Environment Variable:** `URLHAUS_API_KEY` in `backend/.env`.

### Refresh Frequency
- **Default Ingestion Interval:** Every 60 minutes via background scheduler.
- **Manual Trigger:** `python -m app.ingestors.run --source urlhaus --limit 20`

### Collected Data Fields
| Raw URLhaus Field | ThreatView Schema Field | Normalization & Handling |
|---|---|---|
| `url` | `indicator` | Normalized via `normalize_indicator` (lowercase scheme & netloc, validated structure) |
| `"url"` | `indicator_type` | Standard canonical type: `"url"` |
| `threat`, `tags` | `category` | Inferred as `c2` (if botnet/c2 tags exist), `phishing`, or `malware` (default for malware downloads) |
| `dateadded` | `first_seen`, `last_seen` | Converted from `YYYY-MM-DD HH:MM:SS UTC` string into timezone-aware UTC datetime |
| `id` | `source_record_id` | URLhaus numeric ID (e.g. `3391820`) |
| `urlhaus_reference` | `source_reference` | Direct link to abuse.ch entry (e.g. `https://urlhaus.abuse.ch/url/3391820/`) |
| `reporter` | `description` | e.g. `"Malicious URL reported by {reporter} (Status: online)"` |
| Complete record | `raw_metadata` | Preserved in `threat_observations.raw_metadata` (JSONB) |

### Rate Limits & Headers
- URLhaus permits automated polling at reasonable frequencies (recommended maximum 1 request per minute for continuous feeds; hourly for standard intervals).
- Non-crashing exception handling on HTTP 401, 403, and 429.

### Attribution Requirements
- Source attribution strictly preserved as `"URLhaus"` with direct reference links to each URL entry on `https://urlhaus.abuse.ch`.

---

## 3. PhishTank (Optional)

- **Source Name:** PhishTank
- **Official Website:** [https://phishtank.org/](https://phishtank.org/)
- **Status:** *Optional feed pending API availability*
