"""
Fetches and parses Transfermarkt's "market values" page for a competition.
""" 

import re
import time 
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.transfermarkt.com"
# Premier League market values, sorted by highest value.
MARKET_VALUES_URL = f"{BASE_URL}/premier-league/marktwerte/wettbewerb/GB1" 

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": f"{BASE_URL}/",
    "Connection": "keep-alive",
}

PLAYER_ID_RE = re.compile(r"spieler/(\d+)")
CLUB_ID_RE = re.compile(r"verein/(\d+)")


def fetch_page(url: str) -> str:
    session = requests.Session()
    session.headers.update(HEADERS)
    session.get(f"{BASE_URL}/", timeout=20)  # warm up, sets cookies
    time.sleep(2)
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_market_value(text: str) -> float | None:
    """Turn '€220.00m' -> 220000000.0, '€850k' -> 850000.0, '-' -> None."""
    text = text.replace("\xa0", "").strip()
    if not text or text == "-":
        return None
    text = text.replace("€", "")
    if text.endswith("m"):
        return float(text[:-1]) * 1_000_000
    if text.endswith("Th.") or text.endswith("k"):
        text = text.replace("Th.", "").replace("k", "")
        return float(text) * 1_000
    try:
        return float(text)
    except ValueError:
        return None


def parse_market_values(html: str) -> list[dict]:
    """Parse the main 'Top market values' table (div#yw1)."""
    soup = BeautifulSoup(html, "lxml")
    container = soup.find("div", id="yw1")
    if container is None:
        raise ValueError("Could not find div#yw1 — page structure may have changed.")

    table = container.find("table", class_="items")
    rows = table.find("tbody").find_all("tr", recursive=False)

    players = []
    for row in rows:
        cells = row.find_all("td", recursive=False)
        if len(cells) < 6:
            continue  # skip anything that doesn't match the expected shape

        player_cell, nationality_cell, age_cell, club_cell, value_cell = (
            cells[1], cells[2], cells[3], cells[4], cells[5]
        )

        player_link = player_cell.select_one('a[href*="/profil/spieler/"]')
        if player_link is None:
            continue
        name = player_link.get_text(strip=True)
        player_id_match = PLAYER_ID_RE.search(player_link["href"])
        transfermarkt_player_id = player_id_match.group(1) if player_id_match else None

        inline_table = player_cell.find("table", class_="inline-table")
        inline_rows = inline_table.find_all("tr")
        position = inline_rows[1].find("td").get_text(strip=True) if len(inline_rows) > 1 else None

        nationality_flags = nationality_cell.find_all("img")
        nationality = nationality_flags[0]["title"] if nationality_flags else None

        age_text = age_cell.get_text(strip=True)
        age = int(age_text) if age_text.isdigit() else None

        club_link = club_cell.find("a")
        club = club_link["title"] if club_link and club_link.has_attr("title") else None
        club_id_match = CLUB_ID_RE.search(club_link["href"]) if club_link else None
        transfermarkt_club_id = club_id_match.group(1) if club_id_match else None

        value_link = value_cell.find("a")
        value_text = value_link.get_text(strip=True) if value_link else value_cell.get_text(strip=True)
        market_value_eur = parse_market_value(value_text)

        players.append({
            "name": name,
            "transfermarkt_player_id": transfermarkt_player_id,
            "position": position,
            "nationality": nationality,
            "age": age,
            "club": club,
            "transfermarkt_club_id": transfermarkt_club_id,
            "market_value_eur": market_value_eur,
        })

    return players