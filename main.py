"""
Entry point: fetch FBref's current Premier League stats, parse them,
and store a fresh snapshot in the database.

Usage:
    python main.py
"""
from datetime import date
from scraper.api_client import current_season, fetch_all_players, PREMIER_LEAGUE_ID
from scraper.dbUtils import init_db, get_connection, get_or_create_player, \
    insert_stats


def run(seasons: list[int] = None) -> None:
    """ 
    Fetch a rolling two-season window: the current season and the previous one.
    since the current is usually incomplete, we want to keep the previous season's data around for context.
    This is a rolling window, not a fixed pair, the next season will be 26/27 and 27/28 automatically, and the 24/25 season will be dropped.
    This is a design choice to keep the database size manageable and relevant.
    """
    if seasons is None:
        current = current_season()
        seasons = [current - 1, current] 

    snapshot_date = date.today().isoformat()
    init_db()
    conn = get_connection() 
    try:
        for season in seasons:
            print(f"Fetching players for season {season}...")
            players = fetch_all_players(PREMIER_LEAGUE_ID, season=season)
            print(f"Fetched {len(players)} players for season {season}. Inserting into database...")

            for player in players:
                player_id = get_or_create_player(conn, player)
                insert_stats(conn, player_id, player["stats"], 
                            season = str(season),
                            snapshot_date=snapshot_date,
                            source="api-football")
            conn.commit()
            print(f"Inserted {len(players)} players for season {season}.")
    finally:
        conn.close()


if __name__ == "__main__":
    run()
