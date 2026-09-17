"""
Test functions for parsing Transfermarkt data

Usage:
    python tests/test_transfermarkt_parsing.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scraper.transfermarkt_scraper import parse_market_values, parse_market_value

FIXTURE_PATH = Path(__file__).parent / "transfermarkt_fixture.html"


def test_parsing():
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    players = parse_market_values(html)

    assert len(players) == 2, f"Expected 2 players, got {len(players)}"

    haaland = players[0]
    assert haaland["name"] == "Erling Haaland"
    assert haaland["transfermarkt_player_id"] == "418560"
    assert haaland["position"] == "Centre-Forward"
    assert haaland["nationality"] == "Norway"
    assert haaland["age"] == 26
    assert haaland["club"] == "Manchester City"
    assert haaland["market_value_eur"] == 220_000_000.0

    rice = players[1]
    assert rice["name"] == "Declan Rice"
    assert rice["nationality"] == "England"  # first flag when dual nationality

    print("All checks passed:")
    print(f"  - parsed {len(players)} players")
    print(f"  - correctly extracted nested inline-table position")
    print(f"  - correctly picked first flag for dual-nationality player")
    print(f"  - haaland: {haaland}")


def test_value_parsing():
    assert parse_market_value("€220.00m") == 220_000_000.0
    assert parse_market_value("€850k") == 850_000.0
    assert parse_market_value("-") is None
    assert parse_market_value("") is None
    print("Value string parsing checks passed.")


if __name__ == "__main__":
    test_parsing()
    test_value_parsing()
