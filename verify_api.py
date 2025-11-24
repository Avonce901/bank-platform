# Hardened verify_api.py - times out quickly and reports clear errors
import requests
import sys
import os

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
TIMEOUT = (5, 7)  # (connect timeout, read timeout)

def get(path="/health"):
    """Make a GET request to the API with timeout and error handling"""
    url = BASE_URL.rstrip("/") + path
    try:
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        return r
    except requests.exceptions.Timeout:
        print(f"ERROR: Timeout when requesting {url}", file=sys.stderr)
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Connection failed to {url}: {e}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request to {url} failed: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    print("============================================================")
    print("🧪 API VERIFICATION TEST")
    print("============================================================")
    print(f"Base URL: {BASE_URL}")
    print()
    
    resp = get("/health")
    if not resp:
        print("❌ Health check failed. See error above.")
        sys.exit(1)
    
    try:
        data = resp.json()
        print("✓ Health check passed!")
        print(f"Response JSON: {data}")
    except ValueError:
        print("✓ Health check returned (non-JSON):")
        print(f"Response text: {resp.text}")
    
    print()
    print("============================================================")
    print("✅ API verification complete")
    print("============================================================")
