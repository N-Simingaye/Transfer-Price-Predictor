"""
Standalone diagnostic: calls API-Football with your existing free key
against a season the free tier DOES cover (2023), and prints the full
raw response for one player so we can see every field actually
available -- not just the subset our current parser extracts.

This doesn't touch the database or the rest of the project.

Usage:
    python scraper/probe_api_football_fields.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.api_client import fetch_players_page, get_api_key, PREMIER_LEAGUE_ID

SEASON_TO_TEST = 2023  # free tier confirmed to cover 2022-2024

api_key = get_api_key()
print(f"Fetching page 1 of Premier League {SEASON_TO_TEST} players...")
data = fetch_players_page(PREMIER_LEAGUE_ID, SEASON_TO_TEST, page=1, api_key=api_key)

print(f"\nPaging info: {data.get('paging')}")

if not data.get("response"):
    print("No players returned -- something's off. Full response:")
    print(json.dumps(data, indent=2)[:2000])
else:
    first_player = data["response"][0]
    print(f"\n--- Full raw entry for {first_player['player']['name']} ---")
    print(json.dumps(first_player, indent=2))

    print("\n--- Top-level statistics keys available (this is what matters) ---")
    stats = first_player["statistics"][0]
    for category, fields in stats.items():
        if isinstance(fields, dict):
            print(f"{category}: {list(fields.keys())}")
        else:
            print(f"{category}: {fields}")