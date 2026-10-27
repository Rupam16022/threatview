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

- **Source Name:** URLhaus
- **Official Website:** [https://urlhaus.abuse.ch/](https://urlhaus.abuse.ch/)
- **Documentation:** [https://urlhaus-api.abuse.ch/](https://urlhaus-api.abuse.ch/)
- **Status:** *Scheduled for Day 4*

*(Documentation will be populated during Day 4 implementation)*

---

## 3. PhishTank (Optional)

- **Source Name:** PhishTank
- **Official Website:** [https://phishtank.org/](https://phishtank.org/)
- **Status:** *Optional feed pending API availability*
