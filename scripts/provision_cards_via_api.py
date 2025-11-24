"""
Call the local endpoint to fetch wallet payloads for each created card.
Usage: python scripts/provision_cards_via_api.py --base http://localhost:8000 --card-ids <id1> <id2> <id3>
"""
import argparse
import requests

parser = argparse.ArgumentParser(description="Fetch wallet provisioning payloads for virtual cards")
parser.add_argument("--base", required=False, default="http://localhost:8000", help="Base URL of the API server")
parser.add_argument("--card-ids", nargs="+", required=True, help="Card IDs to fetch payloads for")
args = parser.parse_args()

print("============================================================")
print("🔧 DEVELOPMENT ONLY: Fetching Wallet Payloads")
print("============================================================")
print(f"Base URL: {args.base}")
print(f"Card IDs: {', '.join(args.card_ids)}")
print()

success_count = 0
error_count = 0

for cid in args.card_ids:
    url = f"{args.base.rstrip('/')}/api/v1/cards/{cid}/wallet_payload"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        payload = r.json()
        print(f"✓ Card {cid}:")
        print(f"  Cardholder: {payload.get('cardholder_name')}")
        print(f"  Last4: {payload.get('last4')}")
        print(f"  Expiry: {payload.get('exp_month')}/{payload.get('exp_year')}")
        print(f"  Token: {payload.get('provisioning_token')}")
        print()
        success_count += 1
    except requests.exceptions.Timeout:
        print(f"✗ Card {cid}: Request timeout")
        error_count += 1
    except requests.exceptions.HTTPError as e:
        print(f"✗ Card {cid}: HTTP error {e.response.status_code}")
        if e.response.status_code == 404:
            print(f"  Card not found")
        else:
            try:
                print(f"  Error: {e.response.json().get('error', 'Unknown error')}")
            except:
                print(f"  Error: {e.response.text}")
        error_count += 1
    except Exception as e:
        print(f"✗ Card {cid}: {e}")
        error_count += 1

print("============================================================")
print(f"Summary: {success_count} successful, {error_count} failed")
print("============================================================")
