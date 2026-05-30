#!/usr/bin/env python3
"""
Configures a fresh local JFrog Artifactory OSS instance:
  1. Waits for Artifactory to be ready
  2. Creates a local PyPI repository called 'pypi-local'
  3. Prints install / publish instructions

Run AFTER:  docker compose up -d
            (give it ~60-90 s to initialise on first boot)

Usage:
    python scripts/setup_jfrog_local.py
    python scripts/setup_jfrog_local.py --base-url http://localhost:8082 --password mypassword
"""

import argparse
import sys
import time

try:
    import requests
except ImportError:
    sys.exit("requests is not installed — run: pip install requests")

DEFAULT_BASE_URL = "http://localhost:8082"
DEFAULT_USER = "admin"
DEFAULT_PASSWORD = "password"
PYPI_REPO = "pypi-local"


def wait_for_artifactory(base_url: str, retries: int = 20, delay: int = 10) -> bool:
    ping = f"{base_url}/artifactory/api/system/ping"
    print(f"Waiting for Artifactory at {base_url} …", flush=True)
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(ping, timeout=5)
            if r.status_code == 200:
                print("  Artifactory is ready.\n")
                return True
        except requests.exceptions.RequestException:
            pass
        print(f"  [{attempt}/{retries}] not ready yet — retrying in {delay}s …")
        time.sleep(delay)
    return False


def create_pypi_repo(base_url: str, user: str, password: str) -> None:
    url = f"{base_url}/artifactory/api/repositories/{PYPI_REPO}"
    payload = {
        "rclass": "local",
        "packageType": "pypi",
        "repoLayoutRef": "simple-default",
        "description": "Local PyPI repository — hello-sdk POC",
    }
    r = requests.put(url, json=payload, auth=(user, password),
                     headers={"Content-Type": "application/json"})
    if r.status_code in (200, 201):
        print(f"Repository '{PYPI_REPO}' created.")
    elif r.status_code == 400 and "already exist" in r.text.lower():
        print(f"Repository '{PYPI_REPO}' already exists — skipping.")
    else:
        print(f"ERROR creating repository [{r.status_code}]: {r.text}", file=sys.stderr)
        sys.exit(1)


def print_summary(base_url: str, user: str, password: str) -> None:
    upload_url = f"{base_url}/artifactory/api/pypi/{PYPI_REPO}/"
    simple_url = f"{base_url}/artifactory/api/pypi/{PYPI_REPO}/simple/"

    print("\n" + "=" * 64)
    print("  Local JFrog Artifactory — setup complete")
    print("=" * 64)
    print(f"  UI:           {base_url}/ui")
    print(f"  Username:     {user}")
    print(f"  Password:     {password}")
    print()
    print("  --- Publish (twine) ---")
    print(f"  pip install build twine")
    print(f"  python -m build")
    print(f"  twine upload --repository-url {upload_url} \\")
    print(f"               -u {user} -p {password} dist/*")
    print()
    print("  --- Install (pip) ---")
    print(f"  pip install hello-sdk \\")
    print(f"    --index-url {simple_url} \\")
    print(f"    --trusted-host localhost")
    print()
    print("  --- Install (uv) ---")
    print(f"  uv add hello-sdk --index-url {simple_url}")
    print("=" * 64 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Set up local JFrog Artifactory for PyPI")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    args = parser.parse_args()

    if not wait_for_artifactory(args.base_url):
        sys.exit("ERROR: Artifactory did not become ready in time.")

    create_pypi_repo(args.base_url, args.user, args.password)
    print_summary(args.base_url, args.user, args.password)


if __name__ == "__main__":
    main()
