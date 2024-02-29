CREATE OR REPLACE TABLE postgres.songs_day_of_week_hour AS 
SELECT 
    artist, 
    title,
    CAST(played_at AS DATE) as played_at,
    day_of_week,
    hour,
    COUNT(*) as ct
FROM sqlite.songs
WHERE 
    service_id=1 
GROUP BY 
    artist, 
    title,
    CAST(played_at AS DATE),
    day_of_week, 
    hour