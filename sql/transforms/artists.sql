CREATE OR REPLACE TABLE postgres.artists AS 
SELECT
    s.artist,
    SUM(s.ct) as total_plays
FROM songs_day_of_week_hour s
WHERE
    s.artist != ''
GROUP BY s.artist
ORDER BY total_plays DESC;

CREATE INDEX IF NOT EXISTS idx_artist 
ON postgres.artists (artist);