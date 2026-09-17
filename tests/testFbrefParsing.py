""" 
test the fbref parsing logic before the live site is ever hit
usage: 
    python tests/testFbrefParsing.py
"""
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.fbrefScraper import extract_commented_table, parse_standard_stats 

FIXTURE_PATH = Path(__file__).parent / "fbrefFixture.html"

def test_extraction_and_parsing():
    html = FIXTURE_PATH.read_text()

    table = extract_commented_table(html, "stats_standard")
    assert table is not None, "Failed to pull table out of the HTML comment"

    players = parse_standard_stats(table)
    assert len(players) == 2, f"Expected 2 players, got {len(players)}"

    striker = players[0]
    assert striker["name"] == "Test Striker"
    assert striker["nationality"] == "ENG"
    assert striker["position"] == "FW"  
    assert striker["stats"]["goals"] == 4.0
    assert striker["stats"]["xg"] == 3.2

    defender = players[1]
    assert defender["name"] == "Test Defender"  
    assert defender["stats"]["goals"] == 0.0 

    print("All checks passed:")
    print(f"  - extracted table from HTML comment correctly")   
    print(f"  - parsed {len(players)} players")
    print(f"  - skipped the repeated header row inside tbody")
    print(f"  - striker stats: {striker['stats']}")
    print(f"  - defender stats: {defender['stats']}")

if __name__ == "__main__":
      test_extraction_and_parsing()



