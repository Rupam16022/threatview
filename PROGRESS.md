# ThreatView Development Progress

**Project:** ThreatView - Cybersecurity Threat Intelligence Dashboard  
**Timeline:** 17 Days  
**Current Phase:** Day 2: First Threat Feed (AlienVault OTX) — Completed & Verified  

---

## 17-Day Roadmap Status

- [x] **Day 1: Project Setup & Health Communications** (VERIFIED)
- [x] **Day 2: First Threat Feed (AlienVault OTX Ingestor & ETL Normalizer)** (VERIFIED)
- [ ] **Day 3: Database Engine (PostgreSQL + SQLAlchemy + Alembic)** (UP NEXT)
- [ ] **Day 4: Second Threat Feed (URLhaus Ingestor & Normalizer)**
- [ ] **Day 5: Background Scheduler (APScheduler)**
- [ ] **Day 6: Backend Dashboard APIs & Stats**
- [ ] **Day 7: Dashboard UI Layout & Metrics (Dark Theme)**
- [ ] **Day 8: Connect Live Database to Dashboard**
- [ ] **Day 9: Charts & Visualizations (Recharts)**
- [ ] **Day 10: Geographic Threat Distribution**
- [ ] **Day 11: Indicator Search Engine (IoC Lookup)**
- [ ] **Day 12: Domain Monitoring & Alerts Engine**
- [ ] **Day 13: Email Notifications System**
- [ ] **Day 14: PDF Threat Reporting (ReportLab)**
- [ ] **Day 15: Production Deployment Prep**
- [ ] **Day 16: Authentication & Tiered Access (Free/Pro)**
- [ ] **Day 17: Final Testing, Polish & Documentation**

---

## Day 2: First Threat Feed (AlienVault OTX) Details

### Completed:
- Built core ETL Indicator Normalization & Validation engine (`backend/app/ingestors/normalizer.py`).
  - Strict type-specific normalization for `ipv4`, `ipv6`, `domain`, `url`, `hash_md5`, `hash_sha1`, `hash_sha256`.
  - Canonical type mapping, domain cleaning (strips accidental protocols and trailing slashes), URL scheme and host normalization.
  - Rejection of corrupt or malformed indicators with descriptive validation errors.
  - Confidence (0-100) and ISO 2-letter country code validation.
- Implemented `AlienVaultOTXIngestor` (`backend/app/ingestors/otx.py`):
  - Connects to official AlienVault OTX REST endpoints (`/pulses/subscribed`, `/pulses/activity`).
  - Supports authentication via `OTX_API_KEY` header (`X-OTX-API-KEY`).
  - Graceful error handling for HTTP 401/403 (informative non-crashing guidance) and HTTP 429 (rate limiting).
  - Normalizes pulse indicators, derives threat category (`c2`, `phishing`, `malware`, `scanning`, `suspicious`) from pulse tags.
  - Preserves source attribution (`source_name`, `source_reference`, `source_record_id`, `description`, `raw_metadata`).
- Created independent CLI test runner (`backend/app/ingestors/run.py`):
  - Can be executed independently via `python -m app.ingestors.run --source otx --limit 5`.
- Documented AlienVault OTX in `docs/THREAT_FEEDS.md`.
- Wrote automated test suites:
  - `backend/tests/test_normalizer.py`: 8 unit tests covering all indicator types, cleaning logic, and validation rules.
  - `backend/tests/test_otx_ingestor.py`: 3 tests with mocked OTX pulse responses, category parsing, and HTTP error handling.
- Updated frontend dashboard roadmap and milestone tracker.

### Tested:
- **Pytest**: Ran `backend/venv/Scripts/python -m pytest tests/` — **13/13 tests passed (100%)**.
- **Ingestion CLI**: Ran `python -m app.ingestors.run --source otx --limit 3` — verified non-crashing graceful authentication notice when API key is unconfigured.
- **Frontend Build**: Ran `npm.cmd run build` — 0 errors, compiled in 510ms.

### Known Issues:
- None.

### Next:
- **Day 3**: Database Architecture (Configure PostgreSQL, build SQLAlchemy ORM models for `threat_indicators`, `threat_observations`, `ingestion_jobs`, `users`, `monitored_domains`, `alerts`, and configure Alembic migrations).
