CREATE OR REPLACE TABLE postgres.songs_min_played_at AS 
SELECT 
    CAST(service_id AS INT) AS service_id,
    artist, 
    title, 
    CAST(MIN(played_at) AS DATETIME) AS played_at
FROM sqlite.songs
WHERE 
    trim(artist) != ''
    AND trim(title) != ''
GROUP BY
    service_id,
    artist,
    title
ORDER BY
    service_id ASC,
    played_at ASC