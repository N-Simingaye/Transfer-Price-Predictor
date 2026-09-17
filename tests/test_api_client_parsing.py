"""
Tests for the API client parsing functions. 

Usage:
    python tests/test_api_client_parsing.py 
"""

import json 
import sys
from pathlib import Path 

sys.path.insert(0, str(Path(__file__).parent.parent)) 

from scraper.api_client import parse_players_page

FIXTURE_PATH = Path(__file__).parent / "api_football_fixture.json"

def test_parsing(): 
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    players = parse_players_page(data)

    # "No Stats Player" has an empty statistics array (didn't play that
    # season) and should be skipped, not crash the parser.
    assert len(players) == 2, f"Expected 2 players, got {len(players)}"

    striker = players[0]
    assert striker["name"] == "Test Striker"
    assert striker["position"] == "Attacker"
    assert striker["stats"]["goals"] == 4.0
    assert striker["stats"]["appearances"] == 5.0

    defender = players[1]
    assert defender["name"] == "Test Defender"
    assert defender["stats"]["goals"] == 0.0

    print("All checks passed:")
    print(f"  - parsed {len(players)} players (skipped the one with no stats)")
    print(f"  - striker: {striker}")
    print(f"  - defender: {defender}") 

if __name__ == "__main__":
    test_parsing()