import argparse
import logging
import sys
from datetime import datetime, timezone
from typing import Dict, Any

from app.database import SessionLocal, check_db_connection
from app.models.threat import IngestionJob
from app.services.threat_service import ThreatService
from app.ingestors.otx import AlienVaultOTXIngestor
from app.ingestors.urlhaus import URLhausIngestor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("IngestorCLI")


def execute_feed_ingestion(source: str, limit: int = 20, verbose: bool = False) -> Dict[str, Any]:
    """
    Ingest indicators from specified OSINT source, persist to PostgreSQL,
    and log an entry in ingestion_jobs.
    """
    print("=" * 70)
    print(f" THREATVIEW — THREAT FEED INGESTION ENGINE")
    print(f" Source: {source.upper()} | Target Limit: {limit}")
    print("=" * 70)

    started_at = datetime.now(timezone.utc)
    db = SessionLocal() if check_db_connection() else None

    # Track job in database
    job_record = None
    if db:
        job_record = IngestionJob(
            source_name=source,
            started_at=started_at,
            status="running",
        )
        db.add(job_record)
        db.commit()

    result = {}
    try:
        if source == "otx":
            with AlienVaultOTXIngestor() as ingestor:
                result = ingestor.ingest_indicators(limit_pulses=limit)
        elif source == "urlhaus":
            with URLhausIngestor() as ingestor:
                result = ingestor.ingest_indicators(limit=limit)
        else:
            raise ValueError(f"Unknown threat source: {source}")

        indicators = result.get("indicators", [])
        status = result.get("status", "unknown")
        error_msg = result.get("error")

        inserted_count = 0
        updated_count = 0

        # Persist normalized indicators to database
        if db and indicators and status == "success":
            counts = ThreatService.save_batch(db, indicators)
            inserted_count = counts["inserted"]
            updated_count = counts["updated"]

        # Update job record in database
        if job_record and db:
            job_record.completed_at = datetime.now(timezone.utc)
            job_record.status = status
            job_record.records_received = len(indicators)
            job_record.records_inserted = inserted_count
            job_record.records_updated = updated_count
            job_record.error_message = error_msg
            db.commit()

        print(f"\n[+] Ingestion Status:       {status.upper()}")
        print(f"[+] Total Indicators Extracted: {len(indicators)}")
        if db:
            print(f"[+] Stored in PostgreSQL:       {inserted_count} new, {updated_count} updated (deduplicated)")
        else:
            print("[!] Database offline: Skipped storage step.")

        if error_msg:
            print(f"\n[-] Feed Notice / Warning: {error_msg}")
            if source == "urlhaus":
                print("    Note: Configure URLHAUS_API_KEY in backend/.env if authenticating with Spamhaus/abuse.ch.")
            elif source == "otx":
                print("    Note: Configure OTX_API_KEY in backend/.env to pull authenticated pulses.")

        if verbose and indicators:
            print("\n--- Sample Extracted Indicators ---")
            for item in indicators[:5]:
                print(f" • [{item['indicator_type'].upper()}] {item['indicator']} (Category: {item['category']})")

        return result

    finally:
        if db:
            db.close()


def main():
    parser = argparse.ArgumentParser(description="ThreatView Threat Feed Ingestion CLI")
    parser.add_argument(
        "--source",
        choices=["otx", "urlhaus", "all"],
        default="all",
        help="Threat intelligence source to ingest (default: all)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Max pulses/records per source (default: 20)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Display sample parsed indicators",
    )

    args = parser.parse_args()

    sources = ["otx", "urlhaus"] if args.source == "all" else [args.source]
    exit_codes = []

    for src in sources:
        res = execute_feed_ingestion(source=src, limit=args.limit, verbose=args.verbose)
        exit_codes.append(0 if res.get("status") == "success" else 1)

    sys.exit(max(exit_codes) if exit_codes else 0)


if __name__ == "__main__":
    main()
