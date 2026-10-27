# ThreatView — Cybersecurity Threat Intelligence Dashboard

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC?style=flat&logo=tailwind-css)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

ThreatView is a modern, full-stack cybersecurity threat intelligence platform built for small-to-medium businesses and security analysts. It collects cybersecurity indicators of compromise (IoCs) from reputable open-source intelligence (OSINT) feeds, normalizes them, and provides an interactive, dark-themed investigation dashboard.

---

## System Architecture

ThreatView utilizes a clean, decoupled 3-tier architecture:
- **Frontend**: React 19, Vite, Tailwind CSS, Lucide React, Recharts, React Router
- **Backend API**: FastAPI (Python 3.12+), Pydantic v2, Uvicorn, HTTPX
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic schema migrations
- **Threat Feeds**: AlienVault OTX, URLhaus (abuse.ch)

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full architectural documentation.

---

## Quickstart: Running Locally

### Prerequisites
- **Python 3.12+** (tested with Python 3.15)
- **Node.js 20+** and **npm**

### 1. Backend Setup

```powershell
# Navigate into backend directory
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1   # (On Windows PowerShell)
# source venv/bin/activate    # (On Linux / macOS)

# Install Python dependencies
pip install -r requirements.txt

# Create .env file from example template
cp .env.example .env

# Run automated tests
pytest tests/

# Start FastAPI development server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- API Base: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/api/health`

---

### 2. Frontend Setup

In a new terminal window:

```powershell
# Navigate into frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

- Frontend Application: `http://localhost:5173`

The frontend Vite server automatically proxies requests sent to `/api/*` to the FastAPI backend at `http://127.0.0.1:8000`.

---

## Project Roadmap

| Phase | Description | Status |
|---|---|---|
| **Day 1** | Project Setup & Health Communications | Completed |
| **Day 2** | Threat Feed 1: AlienVault OTX Ingestion | Up next |
| **Day 3** | Database Models (PostgreSQL + SQLAlchemy + Alembic) | Queued |
| **Day 4** | Threat Feed 2: URLhaus Ingestion & Normalizer | Queued |
| **Day 5** | Background Job Scheduler (APScheduler) | Queued |
| **Day 6** | Dashboard Analytics & Aggregation Endpoints | Queued |
| **Day 7** | Dashboard UI Layout & Metrics Cards | Queued |
| **Day 8** | Connecting Real Database Intelligence to Frontend | Queued |
| **Day 9** | Threat Activity & Category Visualizations (Recharts) | Queued |
| **Day 10** | Geographic Indicator Distribution | Queued |
| **Day 11** | IoC Search (IP, Domain, URL) | Queued |
| **Day 12** | Domain Monitoring & Alerting Engine | Queued |
| **Day 13** | Email Notifications System | Queued |
| **Day 14** | Automated Weekly Threat PDF Reports (ReportLab) | Queued |
| **Day 15** | Cloud Deployment Preparation | Queued |
| **Day 16** | User Authentication & Tiered Access (Free vs Pro) | Queued |
| **Day 17** | Final Audit, Performance Optimization & Polish | Queued |

---

## Testing

Run backend automated tests:

```powershell
cd backend
.\venv\Scripts\python -m pytest tests/ -v
```

---

## Disclaimer

ThreatView is an intelligence aggregation and investigation tool. A threat feed match constitutes evidence for investigation, not definitive proof that an indicator is compromised or actively malicious.
