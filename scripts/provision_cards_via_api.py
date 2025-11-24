"""
Call the local endpoint to fetch wallet payloads for each created card.
Usage: python scripts/provision_cards_via_api.py --base http://localhost:8000 --card-ids 1 2 3
"""
import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--base", required=False, default="http://localhost:8000", help="Base URL")
parser.add_argument("--card-ids", nargs="+", type=int, required=True, help="Card IDs to fetch payloads for")
args = parser.parse_args()

for cid in args.card_ids:
    url = f"{args.base.rstrip('/')}/cards/{cid}/wallet_payload/"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        print(f"Card {cid} payload: {r.json()}")
    except Exception as e:
        print(f"Failed to fetch card {cid}: {e}")
