# THREATVIEW
## AI Development Specification
### Cybersecurity Threat Intelligence Dashboard

Project Name: ThreatView
Project Type: Full-Stack Cybersecurity SaaS Application
Development Duration: 17 Days
Development Approach: AI-Assisted Development
Primary IDE: Google Antigravity
Target: Functional, deployed, demonstrable application

---

# 1. AI AGENT INSTRUCTIONS

You are a senior full-stack software engineer, cybersecurity engineer,
database architect, UI/UX designer, and technical mentor.

Your task is to build a complete cybersecurity threat intelligence
dashboard called ThreatView.

The developer is a beginner and has 17 days to complete the project.

Your responsibilities:

1. Design a maintainable full-stack architecture.
2. Implement production-quality code appropriate for an MVP.
3. Explain important technical decisions in beginner-friendly language.
4. Build features incrementally.
5. Verify that code works before proceeding.
6. Use real cybersecurity threat intelligence APIs.
7. Never present fabricated threat information as real.
8. Handle API failures and unavailable services gracefully.
9. Implement secure configuration practices.
10. Maintain clear documentation.
11. Prioritize the core functionality over unnecessary complexity.
12. Keep the application deployable throughout development.
13. Do not introduce unnecessary paid dependencies.
14. Do not implement fake buttons or nonfunctional features.
15. Ask for credentials only when necessary, and never request that
    secrets be pasted into source files or committed to Git.

IMPORTANT:

Do not generate the entire application in one unverified step.

Implement the project phase by phase.

After completing each milestone:
- Run the application.
- Test the implemented functionality.
- Fix errors.
- Explain what was completed.
- Explain how to verify it.
- Update the project progress file.

Create a PROGRESS.md file and maintain it throughout development.

---

# 2. PROJECT OVERVIEW

ThreatView is a cybersecurity threat intelligence platform designed
for small and medium-sized businesses.

It collects cybersecurity indicators from open-source intelligence
(OSINT) feeds and presents them through an interactive dashboard.

The application helps users:

- Monitor recently reported cybersecurity threats.
- Explore suspicious IP addresses.
- Investigate malicious domains and URLs.
- Understand trends in collected threat intelligence.
- Search indicators of compromise.
- Monitor their business domains.
- Receive notifications when matching indicators appear.
- Generate cybersecurity intelligence reports.
- Access features according to subscription tiers.

ThreatView is an intelligence aggregation and investigation tool.

It is not an intrusion detection system, antivirus engine, or
automatic incident response platform.

A threat feed match is evidence for investigation, not proof
that an indicator is malicious.

---

# 3. CORE PROJECT OBJECTIVES

The project must implement four major functional phases.

## Phase 1: Threat Intelligence Ingestion

Build a backend service that collects threat data from external feeds.

Requirements:

- Connect to at least two real threat intelligence sources.
- Extract indicators.
- Normalize the collected information.
- Store normalized records.
- Prevent duplicate records.
- Track source attribution.
- Schedule periodic updates.
- Log ingestion activity.
- Handle API errors and rate limits.

## Phase 2: Intelligence Dashboard

Build a React dashboard displaying:

- Total stored indicators.
- Newly collected indicators.
- Malicious or suspicious IP indicators.
- Malicious URL indicators.
- Threat activity charts.
- Indicator category distribution.
- Geographic distribution where available.
- Recently collected indicators.
- Data freshness information.

## Phase 3: Search and Alerts

Implement:

- Searchable indicator database.
- Exact IP address searches.
- Domain searches.
- URL searches.
- Threat details pages.
- Domain monitoring.
- Alert history.
- Email notifications.

## Phase 4: Reports and Tiered Access

Implement:

- Weekly threat intelligence PDF reports.
- CSV export.
- Free and Pro access restrictions.
- Authentication.
- Historical search restrictions.
- Documentation.
- Cloud deployment.

---

# 4. TECHNOLOGY STACK

Use the following technologies unless a strong technical reason
requires an alternative.

## Frontend

Framework: React.js
Build Tool: Vite
Language: JavaScript
Styling: Tailwind CSS
Charts: Recharts
Icons: Lucide React
API Client: Axios
Routing: React Router

## Backend

Language: Python 3.12+
Framework: FastAPI
Server: Uvicorn
ORM: SQLAlchemy
Validation: Pydantic
HTTP Client: HTTPX
Database Migrations: Alembic

## Database

PostgreSQL

## Background Processing

APScheduler for local development.

For production, use a dedicated scheduler process or managed
scheduled jobs.

Do not run duplicate scheduler instances inside multiple
web workers.

## Reports

ReportLab

## Authentication

Use secure password hashing and token-based authentication.

Authentication must be implemented server-side.

## Deployment

Frontend: Vercel
Backend: Render or equivalent Python hosting
Database: Managed PostgreSQL
Scheduler: Dedicated worker or managed scheduled job

Verify current platform pricing, free-tier limitations,
and background-job support before deployment.

---

# 5. SYSTEM ARCHITECTURE

Implement this architecture:

External Threat Intelligence Sources
             |
             v
      Python Ingestors
             |
             v
       ETL Normalizer
             |
             v
       PostgreSQL DB
             |
             v
        FastAPI API
             |
             v
       React Frontend
             |
             v
        End Users

Additional services:

Scheduler -> Ingestion Engine

Alert Engine -> Email Provider

Report Generator -> PDF Download

Authentication -> Role/Plan Authorization

The frontend must not communicate directly with private
third-party threat intelligence APIs.

Private API keys must remain on the backend.

---

# 6. THREAT INTELLIGENCE SOURCES

Integrate the following sources.

## Source 1: AlienVault OTX

Website:
https://otx.alienvault.com/

Purpose:

Collect threat intelligence indicators from available OTX
pulses and supported endpoints.

Potential data:

- IPv4 indicators.
- IPv6 indicators.
- Domains.
- URLs.
- File hashes.
- Pulse metadata.
- Threat tags.

Requirements:

- Use documented endpoints.
- Authenticate using environment variables.
- Respect rate limits.
- Handle pagination.
- Preserve source attribution.
- Record relevant timestamps.

Do not assume every indicator has reliable severity,
country, or industry-targeting metadata.

## Source 2: URLhaus

Website:
https://urlhaus.abuse.ch/

Purpose:

Collect malicious URL intelligence.

Potential data:

- URL.
- Host.
- Detection timestamps.
- URL status.
- Threat classification.
- Associated metadata.

Requirements:

- Consult current official API/download documentation.
- Respect access requirements and rate limits.
- Use permitted endpoints or feeds.
- Normalize URLs.
- Preserve source information.

## Optional Source 3: PhishTank

Website:
https://phishtank.org/

Integrate only if access is available and reliable.

Do not block project progress while waiting for access.

## Feed Documentation

Create:

docs/THREAT_FEEDS.md

Document:

- Source name.
- Official website.
- Endpoint or feed used.
- Authentication requirements.
- Refresh frequency.
- Data fields collected.
- Rate limits.
- Known limitations.
- Attribution requirements.

---

# 7. ETL PIPELINE

ETL stands for:

Extract
Transform
Load

Implement independent ingestor modules.

## Extract

Download information from external sources.

Requirements:

- HTTP timeouts.
- Retry with backoff.
- Rate-limit awareness.
- Pagination where appropriate.
- Error logging.
- Request status tracking.

## Transform

Convert different source formats into a unified schema.

Normalized indicator example:

{
  "indicator": "192.0.2.10",
  "indicator_type": "ipv4",
  "source": "ExampleFeed",
  "category": "suspicious",
  "confidence": null,
  "country_code": null,
  "first_seen": null,
  "last_seen": null,
  "collected_at": "2026-10-27T10:00:00Z"
}

This is illustrative data.

192.0.2.10 is a documentation IP address.

Do not treat this example as a real threat.

## Load

Store normalized records in PostgreSQL.

Requirements:

- Validate indicator formats.
- Reject malformed records.
- Prevent unnecessary duplicate storage.
- Preserve multiple source observations.
- Use timezone-aware timestamps.
- Track ingestion errors.
- Use database transactions appropriately.

Do not invent missing source metadata.

Unknown values must remain null or explicitly unknown.

---

# 8. DATABASE DESIGN

Use PostgreSQL with SQLAlchemy models and Alembic migrations.

Create the following tables.

## Table: threat_indicators

Fields:

id: UUID primary key

indicator: TEXT

indicator_type: VARCHAR

category: VARCHAR nullable

confidence: INTEGER nullable

country_code: VARCHAR nullable

first_seen: TIMESTAMP nullable

last_seen: TIMESTAMP nullable

created_at: TIMESTAMP

updated_at: TIMESTAMP

Requirements:

- Index indicator.
- Index indicator_type.
- Index created_at.
- Support efficient searches.
- Use UTC timestamps.

## Table: threat_observations

Fields:

id: UUID primary key

indicator_id: UUID foreign key

source_name: VARCHAR

source_reference: TEXT nullable

source_record_id: TEXT nullable

description: TEXT nullable

raw_metadata: JSONB

observed_at: TIMESTAMP nullable

collected_at: TIMESTAMP

Purpose:

Preserve evidence and attribution from individual feeds.

The same indicator can appear in multiple feeds.

Do not overwrite source-specific evidence.

Implement a practical uniqueness strategy for source records.

## Table: ingestion_jobs

Fields:

id: UUID primary key

source_name: VARCHAR

started_at: TIMESTAMP

completed_at: TIMESTAMP nullable

status: VARCHAR

records_received: INTEGER

records_inserted: INTEGER

records_updated: INTEGER

error_message: TEXT nullable

Purpose:

Track scheduled ingestion activity.

## Table: users

Fields:

id: UUID primary key

email: VARCHAR unique

password_hash: TEXT

organization_name: VARCHAR nullable

industry: VARCHAR nullable

subscription_plan: VARCHAR

created_at: TIMESTAMP

## Table: monitored_domains

Fields:

id: UUID primary key

user_id: UUID foreign key

domain: VARCHAR

created_at: TIMESTAMP

is_active: BOOLEAN

## Table: alerts

Fields:

id: UUID primary key

user_id: UUID foreign key

indicator_id: UUID foreign key

alert_type: VARCHAR

message: TEXT

created_at: TIMESTAMP

email_sent: BOOLEAN

read_status: BOOLEAN

Requirements:

- Define relationships properly.
- Add appropriate indexes.
- Use migrations rather than manually modifying
  production tables.
- Avoid storing unnecessary personal information.

---

# 9. BACKEND PROJECT STRUCTURE

Use this structure:

threatview/
|
|-- backend/
|   |
|   |-- app/
|   |   |
|   |   |-- main.py
|   |   |-- config.py
|   |   |-- database.py
|   |   |
|   |   |-- models/
|   |   |   |-- threat.py
|   |   |   |-- user.py
|   |   |   |-- alert.py
|   |   |
|   |   |-- schemas/
|   |   |   |-- threat.py
|   |   |   |-- user.py
|   |   |
|   |   |-- routes/
|   |   |   |-- dashboard.py
|   |   |   |-- threats.py
|   |   |   |-- search.py
|   |   |   |-- alerts.py
|   |   |   |-- reports.py
|   |   |   |-- auth.py
|   |   |
|   |   |-- ingestors/
|   |   |   |-- otx.py
|   |   |   |-- urlhaus.py
|   |   |   |-- normalizer.py
|   |   |
|   |   |-- services/
|   |   |   |-- threat_service.py
|   |   |   |-- alert_service.py
|   |   |   |-- report_service.py
|   |   |
|   |   |-- scheduler/
|   |   |   |-- jobs.py
|   |   |
|   |   |-- utils/
|   |
|   |-- tests/
|   |-- alembic/
|   |-- requirements.txt
|   |-- .env.example
|
|-- frontend/
|
|-- docs/
|
|-- README.md
|
|-- PROGRESS.md
|
|-- THREATVIEW_PROJECT_SPEC.md

Adjust filenames where necessary while preserving modular separation.

---

# 10. BACKEND API ENDPOINTS

Implement REST APIs.

## Health

GET /api/health

Returns backend health status.

## Dashboard Statistics

GET /api/dashboard/stats

## Recent Indicators

GET /api/threats/recent

## Threat Details

GET /api/threats/{id}

## Indicator Search

GET /api/search?indicator=example.com

## Trends

GET /api/dashboard/trends

## Category Distribution

GET /api/dashboard/categories

## Geographic Distribution

GET /api/dashboard/countries

## Authentication

POST /api/auth/register
POST /api/auth/login
GET /api/auth/me

## Domain Monitoring

GET /api/monitored-domains
POST /api/monitored-domains
DELETE /api/monitored-domains/{id}

## Alerts

GET /api/alerts
PATCH /api/alerts/{id}/read

## Reports

GET /api/reports/weekly

## CSV Export

GET /api/export/csv

---

# 25. DEVELOPMENT TIMELINE

Follow the 17-day plan:
- DAY 1: Project Setup
- DAY 2: First Threat Feed (AlienVault OTX)
- DAY 3: Database (PostgreSQL + SQLAlchemy + Alembic)
- DAY 4: Second Threat Feed (URLhaus)
- DAY 5: Scheduler (APScheduler)
- DAY 6: Backend Dashboard APIs
- DAY 7: Dashboard UI
- DAY 8: Connect Real Data
- DAY 9: Charts (Recharts)
- DAY 10: Geographic Visualization
- DAY 11: Indicator Search
- DAY 12: Domain Monitoring
- DAY 13: Email Notifications
- DAY 14: PDF Reporting
- DAY 15: Deployment
- DAY 16: Authentication and Tiered Access
- DAY 17: Final Testing and Documentation
