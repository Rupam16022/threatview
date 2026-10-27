# ThreatView Development Progress

**Project:** ThreatView - Cybersecurity Threat Intelligence Dashboard  
**Timeline:** 17 Days  
**Current Phase:** Day 5: Background Scheduler (APScheduler) — Completed & Verified  

---

## 17-Day Roadmap Status

- [x] **Day 1: Project Setup & Health Communications** (VERIFIED)
- [x] **Day 2: First Threat Feed (AlienVault OTX Ingestor & ETL Normalizer)** (VERIFIED)
- [x] **Day 3: Database Engine (PostgreSQL + SQLAlchemy + Alembic)** (VERIFIED)
- [x] **Day 4: Second Threat Feed (URLhaus Ingestor & De-duplication)** (VERIFIED)
- [x] **Day 5: Background Scheduler (APScheduler & Concurrency Locking)** (VERIFIED)
- [ ] **Day 6: Backend Dashboard APIs & Stats** (UP NEXT)
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

## Day 5: Background Scheduler (APScheduler) Details

### Completed:
- Implemented **ThreatFeedScheduler** (`backend/app/scheduler/jobs.py`):
  - Uses `APScheduler` background scheduler configured with 60-minute default interval (`INGESTION_INTERVAL_MINUTES=60`).
  - Added dedicated per-source mutex locks (`_locks = {"otx": Lock(), "urlhaus": Lock()}`) strictly preventing overlapping ingestion runs for the same source.
  - Automatically records every run in `ingestion_jobs` with start, completion, record volume, and error messages.
  - Non-crashing exception handling: if a threat feed fails or rate limits, the failure is cleanly recorded in the database while the scheduler and web server continue operating smoothly.
  - Provides dual operational modes:
    1. Single-process local development mode (managed via FastAPI `lifespan` in `app/main.py`).
    2. Dedicated standalone background worker process (`python -m app.scheduler.jobs`) suitable for containerized and production deployments.
- Created Scheduler REST API endpoints (`backend/app/routes/scheduler.py`):
  - `GET /api/scheduler/status`: Returns live running state, active jobs, intervals, and upcoming execution timestamps.
  - `GET /api/scheduler/jobs`: Returns logged ingestion history directly from PostgreSQL.
  - `POST /api/scheduler/trigger/{source}`: Dispatches on-demand ingestion for `otx` or `urlhaus` asynchronously.
- Wrote automated tests in `backend/tests/test_scheduler.py`:
  - `test_scheduler_lifecycle`: Validated scheduler startup, job registry, and clean shutdown.
  - `test_overlapping_run_prevention`: Verified that concurrent execution requests for the same source are safely skipped.
  - `test_scheduler_status_api`: Verified the `/api/scheduler/status` endpoint.
  - `test_scheduler_jobs_history_api`: Verified the `/api/scheduler/jobs` endpoint.
  - `test_scheduler_trigger_api`: Verified background job queueing and 400 error handling on invalid sources.
- Updated frontend dashboard UI with Day 5 completion badge and roadmap tracking.

### Tested:
- **Pytest**: Ran `backend/venv/Scripts/python -m pytest tests/` — **25/25 tests passed (100%)**.
- **Live Scheduler API**: Queried `GET http://localhost:5173/api/scheduler/status` &mdash; returned `{"scheduler_running": true, "active_jobs_count": 2}`.
- **Frontend Build**: `npm run build` compiled cleanly in 430ms.

### Known Issues:
- None.

### Next:
- **Day 6**: Backend Dashboard APIs (Implement `/api/dashboard/stats`, `/api/threats/recent`, `/api/dashboard/trends`, `/api/dashboard/categories`, `/api/dashboard/countries`, and add API tests).
