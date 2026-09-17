-- Core identity tables (stable, rarely change)

CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    dob TEXT,                  -- ISO date, e.g. '1998-06-15'
    nationality TEXT,
    primary_position TEXT      -- GK / DF / MF / FW
);

CREATE TABLE IF NOT EXISTS clubs (
    club_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    league TEXT
);

-- Maps our internal player_id to each external source's own ID.
-- This is the entity-resolution table: FBref and Transfermarkt each
-- have their own IDs for the same human, and we link them here once,
-- so we never have to re-resolve a player after the first match.
CREATE TABLE IF NOT EXISTS source_ids (
    player_id INTEGER NOT NULL REFERENCES players(player_id),
    source TEXT NOT NULL,             -- 'fbref' | 'transfermarkt'
    source_player_id TEXT NOT NULL,
    PRIMARY KEY (source, source_player_id)
);

-- Long/tidy fact table: one row per stat per snapshot.
-- No NULLs, no schema migration needed when we add a new stat later.
CREATE TABLE IF NOT EXISTS player_stats (
    player_id INTEGER NOT NULL REFERENCES players(player_id),
    season TEXT NOT NULL,             -- e.g. '2025-2026'
    snapshot_date TEXT NOT NULL,      -- date this row was scraped
    stat_name TEXT NOT NULL,          -- e.g. 'goals', 'xg', 'tackles'
    stat_value REAL,
    source TEXT NOT NULL,
    PRIMARY KEY (player_id, season, snapshot_date, stat_name, source)
);

-- Separate from player_stats: different source, different shape
-- (always a single number), appended every snapshot so we can see
-- value trend over time going into a transfer window.
CREATE TABLE IF NOT EXISTS player_valuations (
    player_id INTEGER NOT NULL REFERENCES players(player_id),
    snapshot_date TEXT NOT NULL,
    club_id INTEGER REFERENCES clubs(club_id),
    market_value_eur REAL,
    PRIMARY KEY (player_id, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_stats_player ON player_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_valuations_player ON player_valuations(player_id);
