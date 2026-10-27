import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.database import SessionLocal, check_db_connection
from app.models.threat import IngestionJob
from app.services.threat_service import ThreatService
from app.ingestors.otx import AlienVaultOTXIngestor
from app.ingestors.urlhaus import URLhausIngestor

logger = logging.getLogger("ThreatScheduler")


class ThreatFeedScheduler:
    """
    Automated Background Scheduler for periodic threat intelligence ingestion.
    Prevents overlapping executions, logs job history to PostgreSQL, and ensures high resilience.
    """

    def __init__(self, interval_minutes: Optional[int] = None):
        self.interval_minutes = interval_minutes or settings.INGESTION_INTERVAL_MINUTES
        self.scheduler = BackgroundScheduler(daemon=True)
        # Mutex locks per feed source to prevent overlapping runs
        self._locks: Dict[str, threading.Lock] = {
            "otx": threading.Lock(),
            "urlhaus": threading.Lock(),
        }
        self._is_initialized = False

    def run_ingestion_job(self, source: str, limit: int = 50) -> Dict[str, Any]:
        """
        Execute an ingestion job for a given threat source.
        Guarantees that overlapping runs for the same source are safely skipped.
        """
        source = source.lower()
        if source not in self._locks:
            self._locks[source] = threading.Lock()

        lock = self._locks[source]
        acquired = lock.acquire(blocking=False)
        if not acquired:
            logger.warning(
                f"[SCHEDULER] Ingestion for '{source}' is already in progress. "
                "Skipping overlapping execution."
            )
            return {
                "source": source,
                "status": "skipped",
                "reason": "overlapping_run_prevented",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        started_at = datetime.now(timezone.utc)
        logger.info(f"[SCHEDULER] Starting scheduled ingestion for '{source}'...")

        db = None
        job_record = None
        if check_db_connection():
            db = SessionLocal()
            job_record = IngestionJob(
                source_name=source,
                started_at=started_at,
                status="running",
            )
            db.add(job_record)
            db.commit()

        summary: Dict[str, Any] = {
            "source": source,
            "started_at": started_at.isoformat(),
            "status": "failed",
            "records_received": 0,
            "records_inserted": 0,
            "records_updated": 0,
            "error": None,
        }

        try:
            # 1. Extract from the specified threat feed
            if source == "otx":
                with AlienVaultOTXIngestor() as ingestor:
                    feed_result = ingestor.ingest_indicators(limit_pulses=5)
            elif source == "urlhaus":
                with URLhausIngestor() as ingestor:
                    feed_result = ingestor.ingest_indicators(limit=limit)
            else:
                raise ValueError(f"Unsupported threat source: '{source}'")

            indicators = feed_result.get("indicators", [])
            feed_status = feed_result.get("status", "failed")
            error_msg = feed_result.get("error")

            summary["records_received"] = len(indicators)
            summary["status"] = feed_status
            summary["error"] = error_msg

            # 2. Persist to PostgreSQL if database is reachable
            if db and indicators and feed_status == "success":
                counts = ThreatService.save_batch(db, indicators)
                summary["records_inserted"] = counts["inserted"]
                summary["records_updated"] = counts["updated"]
                logger.info(
                    f"[SCHEDULER] Successfully ingested {len(indicators)} indicators from {source} "
                    f"({counts['inserted']} inserted, {counts['updated']} updated)."
                )
            elif error_msg:
                logger.warning(f"[SCHEDULER] Notice during {source} ingestion: {error_msg}")

            # 3. Update job record in database
            if job_record and db:
                job_record.completed_at = datetime.now(timezone.utc)
                job_record.status = feed_status
                job_record.records_received = len(indicators)
                job_record.records_inserted = summary["records_inserted"]
                job_record.records_updated = summary["records_updated"]
                job_record.error_message = error_msg
                db.commit()

        except Exception as exc:
            logger.error(f"[SCHEDULER] Unhandled exception during {source} ingestion: {exc}", exc_info=True)
            summary["status"] = "failed"
            summary["error"] = str(exc)
            if job_record and db:
                job_record.completed_at = datetime.now(timezone.utc)
                job_record.status = "failed"
                job_record.error_message = str(exc)
                db.commit()
        finally:
            if db:
                db.close()
            lock.release()

        return summary

    def start(self):
        """Configure jobs and start the background scheduler."""
        if self._is_initialized and self.scheduler.running:
            return

        logger.info(f"[SCHEDULER] Initializing threat feed schedule (Interval: {self.interval_minutes}m)...")

        # Job 1: AlienVault OTX periodic refresh
        self.scheduler.add_job(
            func=self.run_ingestion_job,
            trigger=IntervalTrigger(minutes=self.interval_minutes),
            args=["otx"],
            id="job_ingest_otx",
            name="AlienVault OTX Feed Ingestion",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )

        # Job 2: URLhaus periodic refresh
        self.scheduler.add_job(
            func=self.run_ingestion_job,
            trigger=IntervalTrigger(minutes=self.interval_minutes),
            args=["urlhaus"],
            id="job_ingest_urlhaus",
            name="URLhaus Feed Ingestion",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )

        self.scheduler.start()
        self._is_initialized = True
        logger.info("[SCHEDULER] Background scheduler active.")

    def shutdown(self):
        """Gracefully shutdown background scheduler."""
        if self.scheduler.running:
            logger.info("[SCHEDULER] Shutting down background scheduler...")
            self.scheduler.shutdown(wait=False)

    def is_running(self) -> bool:
        return self.scheduler.running

    def get_status(self) -> Dict[str, Any]:
        """Return live health and metadata for all scheduled jobs."""
        jobs_info = []
        if self.scheduler.running:
            for job in self.scheduler.get_jobs():
                next_run = job.next_run_time.isoformat() if job.next_run_time else None
                jobs_info.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": next_run,
                    "interval_minutes": self.interval_minutes,
                })

        return {
            "scheduler_running": self.scheduler.running,
            "interval_minutes": self.interval_minutes,
            "active_jobs_count": len(jobs_info),
            "jobs": jobs_info,
        }

    def trigger_now(self, source: str) -> threading.Thread:
        """Trigger an immediate asynchronous ingestion job in a background thread."""
        thread = threading.Thread(
            target=self.run_ingestion_job,
            args=[source],
            daemon=True,
            name=f"manual-ingest-{source}",
        )
        thread.start()
        return thread


# Global scheduler instance
threat_scheduler = ThreatFeedScheduler()


def run_standalone_worker():
    """Entry point for running the scheduler as a dedicated background worker process."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [ThreatWorker] %(message)s",
    )
    print("=" * 65)
    print(" THREATVIEW — DEDICATED BACKGROUND SCHEDULER WORKER")
    print(f" Ingestion Interval: Every {settings.INGESTION_INTERVAL_MINUTES} minutes")
    print("=" * 65)

    threat_scheduler.start()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        threat_scheduler.shutdown()
        print("\n[!] Scheduler worker terminated cleanly.")


if __name__ == "__main__":
    run_standalone_worker()
