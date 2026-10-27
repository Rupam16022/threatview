# ThreatView Development Progress

**Project:** ThreatView - Cybersecurity Threat Intelligence Dashboard  
**Timeline:** 17 Days  
**Current Phase:** Day 3: Database Engine (PostgreSQL + SQLAlchemy + Alembic) — Completed & Verified  

---

## 17-Day Roadmap Status

- [x] **Day 1: Project Setup & Health Communications** (VERIFIED)
- [x] **Day 2: First Threat Feed (AlienVault OTX Ingestor & ETL Normalizer)** (VERIFIED)
- [x] **Day 3: Database Engine (PostgreSQL + SQLAlchemy + Alembic)** (VERIFIED)
- [ ] **Day 4: Second Threat Feed (URLhaus Ingestor & Normalizer)** (UP NEXT)
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

## Day 3: Database Engine (PostgreSQL + SQLAlchemy + Alembic) Details

### Completed:
- Created dedicated `threatview` PostgreSQL database on local PostgreSQL 18 instance.
- Built SQLAlchemy 2.0 ORM models in `backend/app/models/`:
  - `ThreatIndicator`: UUID primary key, indexed `indicator`, `indicator_type`, `category`, `confidence`, `country_code`, `first_seen`, `last_seen`, `created_at`, unique composite constraint on `(indicator, indicator_type)`.
  - `ThreatObservation`: Preserves multi-source evidence and attribution, links to indicator via foreign key (`CASCADE`), `source_name`, `source_reference`, `source_record_id`, `description`, `raw_metadata` (JSONB), and timestamps.
  - `IngestionJob`: Execution metrics, status (`running`, `completed`, `failed`), counts (`received`, `inserted`, `updated`), error logging.
  - `User`: Accounts with role-based subscription tiers (`free` vs `pro`), credentials hashing field, organization and industry.
  - `MonitoredDomain`: User-configured domains for automated alert scanning with active flag.
  - `Alert`: Triggered notifications when ingested indicators match monitored domains, with email delivery and read status tracking.
- Initialized and configured **Alembic** migration management (`backend/alembic/`):
  - Created initial migration revision `2bcfb7b45f0e_create_initial_threatview_schema.py`.
  - Applied migrations via `alembic upgrade head`, generating all 6 relational tables and composite indexes.
- Implemented **ThreatService** (`backend/app/services/threat_service.py`):
  - Deduplication: Checks existing `(indicator, indicator_type)`; updates `last_seen` and category without duplicate row creation.
  - Observation attribution: Records source-specific observation rows linked to the parent indicator.
  - Query methods: `get_recent_indicators`, `get_indicator_by_id`, `search_exact_indicator`, and `get_dashboard_stats`.
- Connected FastAPI `/api/health` to perform real PostgreSQL liveness checks, returning `"database": "connected"`.
- Updated React dashboard UI with live database connectivity status and verified proxy handshake.

### Tested:
- **Pytest**: Ran `backend/venv/Scripts/python -m pytest tests/` — **17/17 tests passed (100%)**.
  - `test_database_connection`: Verified active PostgreSQL connectivity.
  - `test_save_indicator_and_deduplication`: Verified indicator insertion, re-ingestion deduplication, and observation linking.
  - `test_get_dashboard_stats`: Verified live database aggregation queries.
  - `test_search_exact_indicator`: Verified indexed query matching.
- **Alembic Migration**: `alembic upgrade head` executed cleanly with 0 errors.
- **Live Health API**: Queried `GET /api/health` returning `{"status": "healthy", "database": "connected"}`.
- **Frontend Build**: `npm run build` compiled cleanly in 395ms.

### Known Issues:
- None.

### Next:
- **Day 4**: Integrate Second Threat Feed (URLhaus by abuse.ch), parse malicious URL feeds, normalize indicators, and store observations into the database with duplicate handling.
