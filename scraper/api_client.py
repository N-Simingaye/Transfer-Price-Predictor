"""
API client for fetchning player stats from API-Football (api-sports.io).
It will return a list of player dicts in the same shape that scraper/dbUtils expects.

Auth: the API key must be set in the environment variable API_SPORTS_KEY.
"""

import os
import time
import requests
from datetime import date 

BASE_URL = "https://v3.football.api-sports.io"
PREMIER_LEAGUE_ID = 39
PAGE_SIZE_DELAY_SECONDS = 1  

def current_season(today: date= None) -> int:
    today = today or date.today()
    return today.year if today.month >= 8 else today.year - 1 

def get_api_key() -> str:
    api_key = os.environ.get("API_SPORTS_KEY").strip()
    if not api_key:
        raise RuntimeError(
            "API_SPORTS_KEY environment variable is not set. "
            "Get a free key at https://dashboard.api-football.com and set it, e.g.:\n"
            "  Windows (PowerShell): $env:API_SPORTS_KEY = 'your-key-here'\n"
            "  macOS/Linux: export API_SPORTS_KEY='your-key-here'"
        )
    return api_key 

def fetch_players_page(league: int, season: int, page: int, api_key: str) -> dict:
    resp = requests.get(
        f"{BASE_URL}/players",
        headers={"x-apisports-key": api_key},
        params={"league": league, "season": season, "page": page},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("errors"):
        raise ValueError(f"API-Football returned errors: {data['errors']}")

    return data 

def parse_players_page(data: dict) -> list[dict]:
    """Reshape one page's response into our common player dict shape."""
    players = []

    for entry in data.get("response", []):
        info = entry.get("player", {})
        stats_entries = entry.get("statistics", [])
        if not stats_entries:
            continue
        primary = stats_entries[0]  

        games = primary.get("games", {}) or {}
        goals = primary.get("goals", {}) or {}

        stats = {}
        if games.get("appearences") is not None:
            stats["appearances"] = float(games["appearences"])
        if games.get("minutes") is not None:
            stats["minutes"] = float(games["minutes"])
        if goals.get("total") is not None:
            stats["goals"] = float(goals["total"])
        if goals.get("assists") is not None:
            stats["assists"] = float(goals["assists"])

        players.append({
            "name": info.get("name"),
            "nationality": info.get("nationality"),
            "position": games.get("position"),
            "api_football_id": info.get("id"),
            "stats": stats,
        }) 
    return players 

def fetch_all_players(league: int = PREMIER_LEAGUE_ID, season: int = None) -> list[dict]:  
    #paginate through all pages of players for the given league and season 
    season = season or current_season()
    api_key = get_api_key()
    all_players = []
    page = 1

    while True: 
        print (f"Fetching page {page}...")
        data = fetch_players_page(league, season, page, api_key)
        all_players.extend(parse_players_page(data))

        paging = data.get("paging", {})
        current, total = paging.get("current", 1), paging.get("total", 1)
        if current >= total:
            break

        page += 1
        time.sleep(PAGE_SIZE_DELAY_SECONDS)  # be polite — don't hammer the API

    return all_players

