CREATE TEMP TABLE blocklist AS
  SELECT TRIM(artist) as blocked_artist FROM read_csv('data/artists_block_list.csv', header=true, delim = ',');

CREATE TEMP TABLE artist_normalized AS
  SELECT TRIM(artist) as artist, TRIM(artist_normalized) as artist_normalized FROM read_csv('data/artist_normalized.csv', header=true, delim = ',');

CREATE TEMP TABLE title_normalized AS
  SELECT TRIM(title) as title, TRIM(title_normalized) as title_normalized FROM read_csv('data/title_normalized.csv', header=true, delim = ',');


CREATE OR REPLACE TABLE postgres.songs_day_of_week_hour AS
SELECT
    CAST(service_id AS INT) as service_id,
    TRIM(sqlite.songs.artist) AS artist,
    LOWER(TRIM(sqlite.songs.artist)) AS artist_lower,
    LOWER(COALESCE(artist_norm.artist_normalized, TRIM(sqlite.songs.artist))) AS artist_normalized,
    TRIM(sqlite.songs.title) AS title,
    LOWER(TRIM(sqlite.songs.title)) AS title_lower,
    LOWER(COALESCE(title_norm.title_normalized, TRIM(sqlite.songs.title))) AS title_normalized,
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
LEFT JOIN artist_normalized artist_norm
    ON sqlite.songs.artist = artist_norm.artist
LEFT JOIN title_normalized title_norm
    ON sqlite.songs.title = title_norm.title
ANTI JOIN blocklist
    ON sqlite.songs.artist = blocklist.blocked_artist
GROUP BY
    service_id,
    sqlite.songs.artist,
    sqlite.songs.title,
    CAST(played_at AS DATE),
    year,
    month,
    week,
    day_of_week,
    hour,
    LOWER(COALESCE(artist_norm.artist_normalized, sqlite.songs.artist)),
    LOWER(COALESCE(title_norm.title_normalized, sqlite.songs.title));

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

-- Indexes for artist_normalized and title_normalized aggregations
CREATE INDEX IF NOT EXISTS played_at_artist_normalized_service_idx
    ON postgres.songs_day_of_week_hour (played_at, artist_normalized, service_id);
CREATE INDEX IF NOT EXISTS played_at_artist_normalized_title_normalized_idx
    ON postgres.songs_day_of_week_hour (played_at, artist_normalized, title_normalized);
CREATE INDEX IF NOT EXISTS service_artist_normalized_title_normalized_idx
    ON postgres.songs_day_of_week_hour (service_id, artist_normalized, title_normalized);