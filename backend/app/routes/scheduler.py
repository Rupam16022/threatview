from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.threat import IngestionJob
from app.scheduler.jobs import threat_scheduler

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])


@router.get("/status")
async def get_scheduler_status():
    """
    Retrieve live background scheduler health, active jobs, and upcoming execution timestamps.
    """
    return threat_scheduler.get_status()


@router.get("/jobs")
async def get_ingestion_history(limit: int = 20, db: Session = Depends(get_db)):
    """
    Fetch recent ingestion job executions, statuses, indicator volumes, and error logs.
    """
    jobs = (
        db.query(IngestionJob)
        .order_by(desc(IngestionJob.started_at))
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(job.id),
            "source_name": job.source_name,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "status": job.status,
            "records_received": job.records_received,
            "records_inserted": job.records_inserted,
            "records_updated": job.records_updated,
            "error_message": job.error_message,
        }
        for job in jobs
    ]


@router.post("/trigger/{source}")
async def trigger_ingestion_job(source: str, background_tasks: BackgroundTasks):
    """
    Manually trigger an asynchronous ingestion run for a specified threat intelligence source.
    """
    clean_src = source.lower()
    if clean_src not in ("otx", "urlhaus"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported threat source: '{source}'. Valid sources: 'otx', 'urlhaus'",
        )

    # Dispatch to background thread
    threat_scheduler.trigger_now(clean_src)

    return {
        "message": f"Ingestion job for '{clean_src}' queued successfully.",
        "source": clean_src,
        "status": "queued",
    }
