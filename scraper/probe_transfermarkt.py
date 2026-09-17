"""
Standalone diagnostic: checks whether Transfermarkt blocks a plain
requests session the way FBref did. Doesn't touch the database or
the rest of the project just tells us what we're dealing with.
"""
import time
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.transfermarkt.com/",
    "Connection": "keep-alive",
}

TARGET_URL = "https://www.transfermarkt.com/premier-league/marktwerte/wettbewerb/GB1"

session = requests.Session()
session.headers.update(HEADERS)

print("Warming up (visiting homepage)...")
session.get("https://www.transfermarkt.com/", timeout=20)
time.sleep(2)

print(f"Fetching {TARGET_URL} ...")
resp = session.get(TARGET_URL, timeout=20)

print(f"Status code: {resp.status_code}")
# Save the full page so we can inspect the real table structure
with open("transfermarkt_sample.html", "w", encoding="utf-8") as f:
    f.write(resp.text)
print(f"Saved {len(resp.text)} characters to transfermarkt_sample.html")

# Quick check: is the actual value table present?
if 'class="items"' in resp.text:
    print("Found a table with class='items' — likely the player value table.")
else:
    print("No 'items' table found — page may need a closer look.")