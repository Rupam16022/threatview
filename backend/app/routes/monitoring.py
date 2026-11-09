"""
Domain Monitoring & In-App Alerts Routes
Lets users register domains to watch and see when they appear in threat feeds.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel, field_validator
import re

from app.database import get_db
from app.models.alert import MonitoredDomain, Alert
from app.models.threat import ThreatIndicator

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

# ── Pydantic schemas ────────────────────────────────────────────────────────

class DomainIn(BaseModel):
    domain: str

    @field_validator("domain")
    @classmethod
    def clean_domain(cls, v: str) -> str:
        v = v.strip().lower()
        # strip scheme if someone pastes a URL
        v = re.sub(r"^https?://", "", v)
        v = v.split("/")[0]  # keep only hostname
        if not v:
            raise ValueError("domain cannot be empty")
        return v


class DomainOut(BaseModel):
    id: str
    domain: str
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}


class AlertOut(BaseModel):
    id: str
    alert_type: str
    message: str
    created_at: str
    read_status: bool
    indicator_value: str | None = None
    indicator_type: str | None = None

    model_config = {"from_attributes": True}


# ── Helpers ─────────────────────────────────────────────────────────────────

# For the MVP we use a fixed demo user UUID (no auth yet — Day 16 adds real auth)
DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"


def _ensure_demo_user(db: Session):
    """Make sure the demo user row exists in the users table."""
    from app.models.user import User
    user = db.query(User).filter(User.id == DEMO_USER_ID).first()
    if not user:
        from datetime import datetime, timezone
        user = User(
            id=DEMO_USER_ID,
            email="demo@threatview.local",
            password_hash="demo_no_auth",
            subscription_plan="pro",
        )
        db.add(user)
        db.commit()
    return user


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/domains", response_model=List[dict])
def list_domains(db: Session = Depends(get_db)):
    """List all monitored domains for the demo user."""
    _ensure_demo_user(db)
    rows = (
        db.query(MonitoredDomain)
        .filter(MonitoredDomain.user_id == DEMO_USER_ID)
        .order_by(desc(MonitoredDomain.created_at))
        .all()
    )
    return [
        {
            "id": str(r.id),
            "domain": r.domain,
            "is_active": r.is_active,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.post("/domains", response_model=dict, status_code=201)
def add_domain(payload: DomainIn, db: Session = Depends(get_db)):
    """Add a domain to the monitoring watchlist."""
    _ensure_demo_user(db)
    # Prevent duplicates
    existing = (
        db.query(MonitoredDomain)
        .filter(
            MonitoredDomain.user_id == DEMO_USER_ID,
            MonitoredDomain.domain == payload.domain,
        )
        .first()
    )
    if existing:
        if not existing.is_active:
            existing.is_active = True
            db.commit()
            return {"id": str(existing.id), "domain": existing.domain, "message": "re-activated"}
        raise HTTPException(status_code=409, detail="Domain already monitored.")

    md = MonitoredDomain(user_id=DEMO_USER_ID, domain=payload.domain)
    db.add(md)
    db.commit()
    db.refresh(md)

    # Immediately scan existing indicators for a match
    _scan_and_create_alerts(db, payload.domain)

    return {"id": str(md.id), "domain": md.domain, "message": "added"}


@router.delete("/domains/{domain_id}", status_code=200)
def remove_domain(domain_id: str, db: Session = Depends(get_db)):
    """Remove (deactivate) a monitored domain."""
    row = db.query(MonitoredDomain).filter(MonitoredDomain.id == domain_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Domain not found.")
    row.is_active = False
    db.commit()
    return {"message": f"Domain '{row.domain}' deactivated."}


@router.get("/alerts", response_model=List[dict])
def list_alerts(db: Session = Depends(get_db)):
    """Return all in-app alerts for the demo user, newest first."""
    _ensure_demo_user(db)
    rows = (
        db.query(Alert)
        .filter(Alert.user_id == DEMO_USER_ID)
        .order_by(desc(Alert.created_at))
        .limit(100)
        .all()
    )
    result = []
    for a in rows:
        ind = db.query(ThreatIndicator).filter(ThreatIndicator.id == a.indicator_id).first()
        result.append({
            "id": str(a.id),
            "alert_type": a.alert_type,
            "message": a.message,
            "created_at": a.created_at.isoformat(),
            "read_status": a.read_status,
            "indicator_value": ind.indicator if ind else None,
            "indicator_type": ind.indicator_type if ind else None,
        })
    return result


@router.post("/alerts/{alert_id}/read", status_code=200)
def mark_alert_read(alert_id: str, db: Session = Depends(get_db)):
    """Mark a single alert as read."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    alert.read_status = True
    db.commit()
    return {"message": "marked as read"}


@router.post("/scan", status_code=200)
def trigger_scan(db: Session = Depends(get_db)):
    """Manually trigger a scan of all monitored domains against the full indicator set."""
    _ensure_demo_user(db)
    domains = (
        db.query(MonitoredDomain)
        .filter(MonitoredDomain.user_id == DEMO_USER_ID, MonitoredDomain.is_active == True)
        .all()
    )
    new_alerts = 0
    for md in domains:
        new_alerts += _scan_and_create_alerts(db, md.domain)
    return {"message": f"Scan complete. {new_alerts} new alert(s) generated."}


# ── Internal helpers ─────────────────────────────────────────────────────────

def _scan_and_create_alerts(db: Session, domain: str) -> int:
    """
    Look for indicators that contain the monitored domain string.
    Creates an Alert row for each new match found.
    """
    from sqlalchemy import func
    matches = (
        db.query(ThreatIndicator)
        .filter(func.lower(ThreatIndicator.indicator).contains(domain.lower()))
        .all()
    )
    new_count = 0
    for ind in matches:
        # Avoid duplicate alerts
        already = (
            db.query(Alert)
            .filter(
                Alert.user_id == DEMO_USER_ID,
                Alert.indicator_id == ind.id,
            )
            .first()
        )
        if already:
            continue
        alert = Alert(
            user_id=DEMO_USER_ID,
            indicator_id=ind.id,
            alert_type="domain_match",
            message=f"Monitored domain '{domain}' matched threat indicator: {ind.indicator} ({ind.indicator_type})",
        )
        db.add(alert)
        new_count += 1
    if new_count:
        db.commit()
    return new_count
