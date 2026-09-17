# Football Transfer Price Predictor

Estimates whether a Premier League player looks under- or over-valued
relative to their market value, by comparing their performance stats
against other players in the same position. Data refreshes on a
schedule so it stays current heading into each transfer window.

**Status: in progress.** Building this in public — see progress below.
See [DEVLOG.md](DEVLOG.md) for the reasoning behind each design decision.

## Why this exists

There's no clean API for transfer valuations, so this project is
built on an honest premise: learn the relationship between player
performance stats (API-Football) and Transfermarkt's own market
value estimates, then use that to flag players whose stats and
valuation seem out of step with their positional peers.

## Design decisions worth reading

- **Long/tidy stats table, not wide.** Player stats vary a lot by
  position (a goalkeeper's meaningful stats aren't a striker's), so
  stats are stored as `(player_id, stat_name, stat_value)` rows
  rather than one column per stat. No schema migration needed when a
  new stat is added later.
- **Snapshots, not overwrites.** Every scrape appends timestamped
  rows instead of overwriting the last one, so value/stat trends
  over time are queryable — not just the latest number.
- **Entity resolution across sources.** Different data sources don't
  share player IDs. A `source_ids` table links them once a match is
  confident, so the expensive matching work never has to repeat for
  a player who's already resolved.
- **Stats come from an API, not a scrape.** FBref sits behind
  Cloudflare's bot-detection challenge, which isn't reliably solvable
  from an unattended, cloud-hosted scheduled job. API-Football trades
  a bit of stat depth (no xG on the free tier) for stats that
  actually stay fresh automatically. Transfermarkt, by contrast, has
  no such protection and is scraped directly for market values.

## Progress

- [x] Schema design (`db/schema.sql`)
- [x] Player stats via API-Football (`scraper/api_client.py`)
- [x] Transfermarkt scraper for market values (`scraper/transfermarkt_scraper.py`)
- [ ] Entity resolution between API-Football and Transfermarkt player IDs
- [ ] Scheduled scraping via GitHub Actions
- [ ] Feature engineering (position-normalized stats)
- [ ] Baseline regression model
- [ ] API + demo UI

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Get a free API-Football key at https://dashboard.api-football.com
(100 requests/day free tier — plenty for this project), then set it
as an environment variable. 

```powershell
# Windows PowerShell
$env:API_SPORTS_KEY = "your-key-here"
```
```bash
# macOS/Linux
export API_SPORTS_KEY="your-key-here"
```

Then run:

```bash
python main.py   # creates the DB if needed, then pulls current Premier League stats
```

## Tests

```bash
python tests/test_api_client_parsing.py
python tests/test_transfermarkt_parsing.py
```

Both run against saved local fixtures, so you can verify the parsing
logic works without hitting a live site or spending API quota every
time you make a change.

## A note on why FBref isn't used

FBref returns a Cloudflare JavaScript challenge (`"Just a moment..."`)
to plain HTTP requests, which cannot be solved without executing
real browser JavaScript. Even a headless-browser workaround would be
unreliable running unattended on GitHub Actions' cloud IPs, which
Cloudflare treats with extra suspicion. See DEVLOG.md for the full
story — `scraper/fbrefscraper.py` is kept in the repo as a record of
that investigation, not because it's currently used.
