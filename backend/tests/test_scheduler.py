import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.scheduler.jobs import ThreatFeedScheduler

client = TestClient(app)


def test_scheduler_lifecycle():
    """Verify scheduler startup, job registry, and graceful shutdown."""
    sched = ThreatFeedScheduler(interval_minutes=15)
    assert not sched.is_running()

    sched.start()
    assert sched.is_running()

    status = sched.get_status()
    assert status["scheduler_running"] is True
    assert status["interval_minutes"] == 15
    assert status["active_jobs_count"] >= 2

    job_ids = [j["id"] for j in status["jobs"]]
    assert "job_ingest_otx" in job_ids
    assert "job_ingest_urlhaus" in job_ids

    sched.shutdown()
    assert not sched.is_running()


def test_overlapping_run_prevention():
    """
    Verify that mutex locking strictly prevents overlapping ingestion runs
    for the same threat feed source.
    """
    sched = ThreatFeedScheduler()

    # Simulate an active job locking 'otx'
    lock = sched._locks["otx"]
    acquired = lock.acquire(blocking=False)
    assert acquired is True

    try:
        # Second call to same source while lock is held must be skipped
        result = sched.run_ingestion_job(source="otx")
        assert result["status"] == "skipped"
        assert result["reason"] == "overlapping_run_prevented"
    finally:
        lock.release()


def test_scheduler_status_api():
    """Verify GET /api/scheduler/status returns active job metadata."""
    response = client.get("/api/scheduler/status")
    assert response.status_code == 200
    data = response.json()
    assert "scheduler_running" in data
    assert "active_jobs_count" in data
    assert "jobs" in data


def test_scheduler_jobs_history_api():
    """Verify GET /api/scheduler/jobs returns logged ingestion job history."""
    response = client.get("/api/scheduler/jobs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_scheduler_trigger_api():
    """Verify POST /api/scheduler/trigger/{source} queues background ingestion."""
    response = client.post("/api/scheduler/trigger/urlhaus")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "urlhaus"
    assert data["status"] == "queued"

    # Bad source returns 400
    bad_resp = client.post("/api/scheduler/trigger/unknown_feed")
    assert bad_resp.status_code == 400
