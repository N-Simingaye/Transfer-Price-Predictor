"""
Scrapes FBref's "standard stats" table for a league and stores it in the long/tidy player_stats table.
fetches the stats and parses them into a list of dicts, one per player. Each dict contains the player's name, nationality
Usage:
    python scraper/fbrefScraper.py
""" 
from bs4 import BeautifulSoup, Comment
import requests

#Premier League "standard stats" page. Table id is stable across seasons.

FBREF_URL = "https://fbref.com/en/comps/9/stats/Premier-League-Stats"
TABLE_ID = "stats_standard"

STAT_COLUMN_MAP = {
    "goals": "goals",
    "assists": "assists", 
    "xg": "xg",
    "xg_assist": "xa",
    "games": "appearances",
    "minutes": "minutes",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        "AppleWebKit/537.36 (KHTML, like Gecko)"
        "Chrome/91.0.4472.124 Safari/537.36"
    ), 

    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://fbref.com/",
    "Connection": "keep-alive",

}

# def fetch_page(url: str) -> str:
#     resp = requests.get(url, headers=HEADERS, timeout=20)
#     resp.raise_for_status()
#     return resp.text

# def fetch_page(url: str) -> str:
#     import time
#     time.sleep(3)  # be polite — don't hammer the server
#     resp = requests.get(url, headers=HEADERS, timeout=20)
#     resp.raise_for_status()
#     return resp.text 

def fetch_page(url: str) -> str:
    import time
    session = requests.Session()
    session.headers.update(HEADERS)

    # Warm up: visit the homepage first so any cookies get set,
    # same as a real browser would before navigating deeper in.
    session.get("https://fbref.com/", timeout=20)
    time.sleep(2)

    resp = session.get(url, timeout=20)
    if resp.status_code == 403:
        print("Still blocked. First 500 chars of response body:")
        print(resp.text[:500])
    resp.raise_for_status()
    return resp.text

def extract_commented_table(html: str, table_id: str) -> BeautifulSoup:
    #this is to find a table that FBref has hidden inside an HTML comment
    soup = BeautifulSoup(html, "lxml")

    # Try the uncommented DOM first, in case FBref changes this behaviour.
    table = soup.find("table", id=table_id)
    if table is not None:
        return table

    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        if table_id in comment:
            comment_soup = BeautifulSoup(comment, "lxml")
            table = comment_soup.find("table", id=table_id)
            if table is not None:
                return table

    raise ValueError(f"Could not find table id={table_id!r} on page, "
                      f"even inside comments. FBref may have changed its markup.")

def parse_standard_stats(table: BeautifulSoup) -> list[dict]:
    #turn the stats table into a list of per-player dicts
    rows = table.find("tbody").find_all("tr")
    players = [] 

    for row in rows:
        #skip rows that are just headers or separators
        if row.get("class") and "thead" in row.get("class"):
            continue 

        name_cell = row.find("td", {"data-stat": "player"})
        if name_cell is None:
            continue 

        player = { 
            "name": name_cell.get_text(strip=True),
            "nationality": _get_stat(row, "nationality"),
            "position": _get_stat(row, "position"),
            "dob": _get_stat(row, "birth_year"),  # FBref only gives birth year here
            "stats": {},
    
        }

        for fbref_key, our_key in STAT_COLUMN_MAP.items():
            value = _get_stat(row, fbref_key)
            if value not in (None, ""):
                try:
                    player["stats"][our_key] = float(value)
                except ValueError:
                    pass 

        players.append(player)        
    return players

def _get_stat(row, data_stat: str) -> str | None:
    cell = row.find("td", {"data-stat": data_stat})
    return cell.get_text(strip=True) if cell else None 