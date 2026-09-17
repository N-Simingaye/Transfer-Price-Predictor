#this file contains the database utils for the scrapper, used by the fbref scrapper and the transfermarket scrapper. 
#the logic is the same for both, so we put it here to avoid code duplication.
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "transfers.db"
SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql" 

def init_db(db_path: Path = DB_PATH) -> None:
    #create the database from schema.sql if it doesn't already exist with these tables. Safe to call every run — CREATE TABLE IF NOT EXISTS means it's a no-op once the schema is in place.
    schema_sql = SCHEMA_PATH.read_text()
    conn = sqlite3.connect(db_path)
    try: 
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    return sqlite3.connect(db_path) 


def get_or_create_player(conn: sqlite3.Connection, player: dict) -> int:
    #find a player by name, or create them. This is deliberately naive (name-only matching) because we're single-source right now. 
    #Once Transfermarkt joins, real entity resolution happens in its own module
    cur = conn.execute(
        "SELECT player_id FROM players WHERE name = ?", (player["name"],)
    )
    row = cur.fetchone()
    if row:
        return row[0]

    cur = conn.execute(
        "INSERT INTO players (name, nationality, primary_position) "
        "VALUES (?, ?, ?)",
        (player["name"], player["nationality"], player["position"]),
    )
    return cur.lastrowid


def insert_stats(conn: sqlite3.Connection, player_id: int, stats: dict,
                  season: str, snapshot_date: str, source: str = "fbref") -> None:
    #INSERT OR REPLACE keyed on ( playerid, season, snapshotDate,statname,source), runs once a day, adds new rows for new days, overwrite existing rows for the same day.
    for stat_name, stat_value in stats.items():
        conn.execute(
            "INSERT OR REPLACE INTO player_stats "
            "(player_id, season, snapshot_date, stat_name, stat_value, source) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (player_id, season, snapshot_date, stat_name, stat_value, source),
        )