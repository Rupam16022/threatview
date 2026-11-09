# ThreatView — Cybersecurity Threat Intelligence Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC?style=flat&logo=tailwind-css)](https://tailwindcss.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon_Cloud-336791?style=flat&logo=postgresql)](https://neon.tech)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

ThreatView is a modern, production-grade cybersecurity threat intelligence platform built for security analysts, incident responders, and organizations. It continuously ingests Indicators of Compromise (IoCs) from OSINT threat feeds, deduplicates and normalizes indicators, tracks multi-feed source attribution, monitors custom domains for security threats, and generates executive PDF intelligence reports.

---

## 🌐 Live Production Deployments

- **Frontend App (Vercel):** [https://threatview-4qowf9niy-rupam16022.vercel.app](https://threatview-4qowf9niy-rupam16022.vercel.app/)
- **Backend API (Render):** [https://threatview-xtk4.onrender.com](https://threatview-xtk4.onrender.com/)
- **Interactive API Documentation:** [https://threatview-xtk4.onrender.com/docs](https://threatview-xtk4.onrender.com/docs)
- **Database:** Serverless PostgreSQL on [Neon](https://neon.tech)

---

## 🚀 Key Features

1. **Live Analytics & Visualization**:
   - 30-day threat trend area chart powered by Recharts.
   - Threat category distribution donut chart.
   - Source feed attribution horizontal bar chart.
   - Real-time database metrics (Total Indicators, 24h New, IPs, URLs).

2. **Indicators Database & Search Engine**:
   - Searchable and paginated indicator catalog with type filters (`ipv4`, `ipv6`, `url`, `domain`, `hash`).
   - Confidence scoring meter and ISO country code flags.
   - Exact-match IoC Lookup engine showing full threat metadata and multi-source observations.

3. **Automated Intelligence Feeds & Scheduler**:
   - Integrated with **AlienVault OTX** and **abuse.ch URLhaus**.
   - Background ingestion engine using **APScheduler** with mutex locking to prevent overlapping runs.
   - Manual feed execution triggers and job execution history audit trail.

4. **Domain Monitoring & In-App Alerts**:
   - Custom domain watchlists for enterprise monitoring.
   - Real-time scanner matching monitored domains against the threat intelligence database.
   - In-app notification alerts with read/unread statuses.

5. **Executive Threat Reporting**:
   - Instant PDF Threat Intelligence Report generator built with **ReportLab**.
   - Generates executive summary tables, category breakdowns, and ingestion metrics for download.

---

## 🏗️ System Architecture

- **Frontend**: React 19, Vite, Tailwind CSS v4, Lucide React, Recharts, React Router v7
- **Backend**: FastAPI (Python 3.12+), Pydantic v2, Uvicorn, APScheduler, ReportLab, HTTPX
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic schema migrations
- **Threat Feeds**: AlienVault OTX (Pulses API) & URLhaus (abuse.ch API)

```
[OSINT Threat Feeds] (OTX, URLhaus)
        │
        ▼
[FastAPI Ingestors + Normalizer] ──► [APScheduler Engine]
        │
        ▼
[PostgreSQL Database (Neon)] ◄─────► [ThreatService Query Layer]
        │
        ▼
[FastAPI REST APIs] (/dashboard, /indicators, /monitoring, /reports)
        │ (CORS Whitelisted)
        ▼
[React 19 Frontend (Vercel)] ◄─────► [Security Analyst / End User]
```

---

## 💻 Local Development Setup

### 1. Backend

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

# Run database migrations
alembic upgrade head

# Run unit and integration tests (25/25 passing)
pytest tests/ -v

# Start backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to explore the dashboard locally.

---

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
