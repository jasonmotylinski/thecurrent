CREATE OR REPLACE TABLE postgres.songs_day_of_week_hour AS 
SELECT 
    CAST(service_id AS INT) as service_id,
    artist, 
    LOWER(artist) AS artist_lower,
    title,
    CAST(played_at AS DATE) as played_at,
    CAST(year AS INT) as year,
    CAST(month AS INT) as month,
    CAST(week AS INT) as week,
    day_of_week,
    CAST(hour AS INT) as hour,
    COUNT(*) as ct
FROM sqlite.songs

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

CREATE INDEX IF NOT EXISTS service_title_played_at_idx ON postgres.songs_day_of_week_hour (service_id, artist, title, played_at);
CREATE INDEX IF NOT EXISTS service_artist_title_idx ON postgres.songs_day_of_week_hour (service_id, artist, title);

-- Exclusives query indexes
CREATE INDEX IF NOT EXISTS played_at_service_artist_idx ON postgres.songs_day_of_week_hour (played_at, service_id, artist);
CREATE INDEX IF NOT EXISTS played_at_artist_service_idx ON postgres.songs_day_of_week_hour (played_at, artist, service_id);
CREATE INDEX IF NOT EXISTS played_at_artist_lower_service_idx ON postgres.songs_day_of_week_hour (played_at, artist_lower, service_id);