CREATE OR REPLACE TABLE postgres.artists AS 
SELECT
    s.artist,
    SUM(s.ct) as total_plays
FROM sqlite.songs s
WHERE
    s.artist != ''
GROUP BY s.artist
ORDER BY total_plays DESC;

CREATE INDEX IF NOT EXISTS idx_artist 
ON postgres.artists (artist);