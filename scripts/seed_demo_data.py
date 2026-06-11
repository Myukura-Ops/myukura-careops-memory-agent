"""Seed synthetic demo data via the API.

Usage:
    python scripts/seed_demo_data.py [--api-url URL] [--access-code CODE]

This script calls the POST /demo/seed API endpoint, which idempotently
creates baseline demographic/clinic entries in MongoDB. The API must
be running before executing this script.
"""
import argparse
import sys

try:
    import httpx
except ImportError:
    print("httpx is required. Install it with: pip install httpx")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Seed synthetic demo data via the API.")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Base URL of the CareOps API (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--access-code",
        default="test-demo-code",
        help="Demo access code for authentication",
    )
    args = parser.parse_args()

    url = f"{args.api_url.rstrip('/')}/demo/seed"
    headers = {"x-demo-access-code": args.access_code}

    print(f"Seeding demo data via {url} ...")
    try:
        resp = httpx.post(url, headers=headers, timeout=30)
        resp.raise_for_status()
        print(f"Success ({resp.status_code}):")
        print(resp.json())
    except httpx.ConnectError:
        print(f"Error: Could not connect to {args.api_url}. Is the API running?")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        print(f"Error: API returned {e.response.status_code}")
        print(e.response.text)
        sys.exit(1)


if __name__ == "__main__":
    main()
