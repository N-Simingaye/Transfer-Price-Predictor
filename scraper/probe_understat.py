"""
Standalone diagnostic: checks whether Understat blocks a plain
requests session, and shows us what the embedded JSON looks like.
Doesn't touch the database or the rest of the project.
"""
import re
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
    "Referer": "https://understat.com/",
    "Connection": "keep-alive",
}

TARGET_URL = "https://understat.com/league/EPL"

session = requests.Session()
session.headers.update(HEADERS)

print("Warming up (visiting homepage)...")
session.get("https://understat.com/", timeout=20)
time.sleep(2)

print(f"Fetching {TARGET_URL} ...")
resp = session.get(TARGET_URL, timeout=20)

print(f"Status code: {resp.status_code}")

with open("understat_sample.html", "w", encoding="utf-8") as f:
    f.write(resp.text)
print(f"Saved {len(resp.text)} characters to understat_sample.html")

# Understat embeds player data as JSON.parse('...') inside a <script> tag.
# Look for the variable that holds player season stats.
match = re.search(r"var\s+playersData\s*=\s*JSON\.parse\('(.+?)'\)", resp.text)
if match:
    print("Found playersData JSON blob — looks like the real page, not a block.")
    print(f"First 300 chars of the encoded blob:")
    print(match.group(1)[:300])
else:
    print("Did NOT find playersData in the response. First 500 chars of body:")
    print(resp.text[:500])