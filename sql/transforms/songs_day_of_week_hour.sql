CREATE TEMP TABLE blocklist AS
  SELECT TRIM(artist) as blocked_artist FROM 'data/artists_block_list.csv';

CREATE OR REPLACE TABLE postgres.songs_day_of_week_hour AS
SELECT
    CAST(service_id AS INT) as service_id,
    artist,
    LOWER(artist) AS artist_lower,
    title,
    LOWER(title) AS title_lower,
    CAST(played_at AS DATE) as played_at,
    CAST(year AS INT) as year,
    CAST(month AS INT) as month,
    CAST(week AS INT) as week,
    day_of_week,
    CASE
        WHEN day_of_week = 'Sunday' THEN 0
        WHEN day_of_week = 'Monday' THEN 1
        WHEN day_of_week = 'Tuesday' THEN 2
        WHEN day_of_week = 'Wednesday' THEN 3
        WHEN day_of_week = 'Thursday' THEN 4
        WHEN day_of_week = 'Friday' THEN 5
        WHEN day_of_week = 'Saturday' THEN 6
        ELSE NULL
    END as day_of_week_int,
    CAST(hour AS INT) as hour,
    COUNT(*) as ct
FROM sqlite.songs
ANTI JOIN blocklist
    ON sqlite.songs.artist = blocklist.blocked_artist
GROUP BY
    service_id,
    artist,
    title,
    CAST(played_at AS DATE),
    year,
    month,
    week,
    day_of_week,
    hour;

-- Indexes for new_last_90_days query
-- Optimizes filtering by service_id + played_at, then partitioning/ordering by artist/title
CREATE INDEX IF NOT EXISTS service_played_at_artist_title_idx
    ON postgres.songs_day_of_week_hour (service_id, played_at, artist, title);

-- Index for efficient filtering on date range
CREATE INDEX IF NOT EXISTS service_id_played_at_idx
    ON postgres.songs_day_of_week_hour (service_id, played_at);

-- Existing indexes for other queries
CREATE INDEX IF NOT EXISTS service_title_played_at_idx ON postgres.songs_day_of_week_hour (service_id, artist, title, played_at);
CREATE INDEX IF NOT EXISTS service_artist_title_idx ON postgres.songs_day_of_week_hour (service_id, artist, title);

-- Exclusives query indexes
CREATE INDEX IF NOT EXISTS played_at_service_artist_idx ON postgres.songs_day_of_week_hour (played_at, service_id, artist);
CREATE INDEX IF NOT EXISTS played_at_artist_service_idx ON postgres.songs_day_of_week_hour (played_at, artist, service_id);
CREATE INDEX IF NOT EXISTS played_at_artist_lower_service_idx ON postgres.songs_day_of_week_hour (played_at, artist_lower, service_id);
CREATE INDEX IF NOT EXISTS played_at_artist_lower_title_lower_idx
    ON postgres.songs_day_of_week_hour (played_at, artist_lower, title_lower);