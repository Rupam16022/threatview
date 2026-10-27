# ThreatView System Architecture

## Architecture Overview

ThreatView is a full-stack cybersecurity threat intelligence platform designed to ingest, normalize, and visualize indicators of compromise (IoCs) including malicious IP addresses, suspicious domains, and malicious URLs from reputable open-source intelligence (OSINT) feeds.

```
       +---------------------------------------------+
       |   OSINT Threat Feeds (External APIs)        |
       |     - AlienVault OTX (Pulses & Indicators)  |
       |     - URLhaus (Malicious URLs)              |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |   Ingestion & ETL Normalization Pipeline    |
       |     - Backend Ingestors                     |
       |     - Indicator Normalizer & De-duplicator  |
       |     - APScheduler Background Worker         |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |   PostgreSQL Data Layer (SQLAlchemy ORM)    |
       |     - threat_indicators                     |
       |     - threat_observations                   |
       |     - ingestion_jobs                        |
       |     - users, monitored_domains, alerts      |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |   FastAPI Asynchronous REST API Engine      |
       |     - Routes: /dashboard, /threats, /search |
       |     - Pydantic Schema Validation            |
       |     - CORS Security Middleware              |
       +---------------------------------------------+
                              ^
                              | (HTTP / REST)
                              v
       +---------------------------------------------+
       |   React 19 + Vite + Tailwind CSS Dashboard  |
       |     - Dark-themed Security UI               |
       |     - Recharts Visualizations               |
       |     - Lucide Security Iconography           |
       +---------------------------------------------+
```

## Security & Architectural Principles

1. **Backend-Mediated Ingestion**: Third-party API keys (e.g. AlienVault OTX, URLhaus) never touch the client browser. All calls are routed securely through the backend.
2. **Defensive Normalization**: Every incoming indicator is parsed, validated, and normalized to prevent database corruption and malicious payload injection.
3. **Investigation Disclaimer**: Threat feed matches are presented as indicators for human analyst triage and investigation, not absolute proof of malicious compromise.
