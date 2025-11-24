# Hardened verify_api.py - times out quickly and reports clear errors
import requests
import sys
import os

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
TIMEOUT = (5, 7)

def get(path="/health"):
    url = BASE_URL.rstrip("/") + path
    try:
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        return r
    except requests.exceptions.Timeout:
        print(f"ERROR: Timeout when requesting {url}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request to {url} failed: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    print("============================================================")
    print("🧪 API VERIFICATION TEST")
    print("============================================================")
    print(f"Base URL: {BASE_URL}")
    resp = get("/health")
    if not resp:
        print("Health check failed. See error above.")
        sys.exit(1)
    try:
        print("Response JSON:", resp.json())
    except ValueError:
        print("Non-JSON health response:", resp.text)
