# ThreatView Development Progress

**Project:** ThreatView - Cybersecurity Threat Intelligence Dashboard  
**Timeline:** 17 Days  
**Current Phase:** Day 4: Second Threat Feed (URLhaus) — Completed & Verified  

---

## 17-Day Roadmap Status

- [x] **Day 1: Project Setup & Health Communications** (VERIFIED)
- [x] **Day 2: First Threat Feed (AlienVault OTX Ingestor & ETL Normalizer)** (VERIFIED)
- [x] **Day 3: Database Engine (PostgreSQL + SQLAlchemy + Alembic)** (VERIFIED)
- [x] **Day 4: Second Threat Feed (URLhaus Ingestor & De-duplication)** (VERIFIED)
- [ ] **Day 5: Background Scheduler (APScheduler)** (UP NEXT)
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

## Day 4: Second Threat Feed (URLhaus) Details

### Completed:
- Implemented **URLhaus Ingestor** (`backend/app/ingestors/urlhaus.py`):
  - Connects to abuse.ch / Spamhaus official REST endpoint (`/v1/urls/recent/`).
  - Supports `Auth-Key` authentication via `URLHAUS_API_KEY`.
  - Non-crashing exception handling on HTTP 401, 403, 429, and `unknown_auth_key`.
  - Parses malicious URLs, reports, threat types, timestamps, and tags into normalized indicator items.
- Enhanced ETL Indicator Normalizer (`backend/app/ingestors/normalizer.py`):
  - Strengthened `normalize_url` validation to require valid IP addresses or domain structures in URL hostnames.
- Upgraded Manual Ingestion CLI (`backend/app/ingestors/run.py`):
  - Supports `--source otx`, `--source urlhaus`, and `--source all`.
  - Persists normalized indicators from both feeds into PostgreSQL in transactional batches.
  - Automatically records ingestion job metadata, counts, and statuses in the `ingestion_jobs` database table.
- Documented URLhaus in `docs/THREAT_FEEDS.md`.
- Wrote automated tests in `backend/tests/test_urlhaus_ingestor.py`:
  - `test_parse_urlhaus_records`: Validated real-world record normalization, category mapping (`c2`, `phishing`, `malware`), and malformed URL filtering.
  - `test_urlhaus_auth_failure_handling`: Verified non-crashing authentication error handling.
  - `test_multi_feed_deduplication_and_attribution`: Verified that two independent feeds (OTX and URLhaus) observing the exact same threat indicator update the single canonical record in `threat_indicators` without duplicate rows, while preserving both source observations in `threat_observations`.
- Updated frontend dashboard UI with Day 4 completed status and roadmap badge.

### Tested:
- **Pytest**: Ran `backend/venv/Scripts/python -m pytest tests/` — **20/20 tests passed (100%)**.
- **CLI Runner**: Verified `python -m app.ingestors.run --source urlhaus --limit 5` successfully records the execution in `ingestion_jobs` table.
- **Frontend Build**: `npm run build` compiled with 0 errors.

### Known Issues:
- None.

### Next:
- **Day 5**: Background Scheduler (Integrate APScheduler to run periodic threat feed updates every 60 minutes, prevent overlapping ingestion jobs, and log history).
