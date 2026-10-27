import argparse
import json
import sys
from app.ingestors.otx import AlienVaultOTXIngestor


def run_otx_ingestion(limit: int = 5, verbose: bool = False):
    """Run manual OTX ingestion and print summary statistics."""
    print("=" * 65)
    print(" THREATVIEW — MANUAL THREAT FEED INGESTION")
    print(f" Source: AlienVault OTX | Limit: {limit} pulses")
    print("=" * 65)

    with AlienVaultOTXIngestor() as ingestor:
        result = ingestor.ingest_indicators(limit_pulses=limit)

    status = result["status"]
    print(f"\n[+] Status: {status.upper()}")
    print(f"[+] Pulses Processed:     {result['pulses_processed']}")
    print(f"[+] Indicators Received:  {result['indicators_extracted']}")
    print(f"[+] Indicators Normalized:{result['indicators_normalized']}")

    if result.get("error"):
        print(f"\n[-] Ingestion Notice / Error: {result['error']}")
        print("[!] Note: AlienVault OTX requires a free API key from https://otx.alienvault.com")
        print("    Set OTX_API_KEY in backend/.env to run live pulls against your account.")

    if verbose and result["indicators"]:
        print("\n--- Sample Normalized Indicators ---")
        for item in result["indicators"][:5]:
            print(f"- [{item['indicator_type'].upper()}] {item['indicator']} (Category: {item['category']})")

    return 0 if status == "success" else 1


def main():
    parser = argparse.ArgumentParser(description="ThreatView Threat Feed Ingestion CLI")
    parser.add_argument(
        "--source",
        choices=["otx", "urlhaus", "all"],
        default="otx",
        help="Threat intelligence source to ingest (default: otx)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum pulses/records to fetch (default: 5)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print sample normalized indicators",
    )

    args = parser.parse_args()

    if args.source == "otx":
        exit_code = run_otx_ingestion(limit=args.limit, verbose=args.verbose)
        sys.exit(exit_code)
    else:
        print(f"Source '{args.source}' scheduled for subsequent milestones.")
        sys.exit(0)


if __name__ == "__main__":
    main()
