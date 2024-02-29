CREATE OR REPLACE TABLE postgres.artists_day_of_week_hour AS 
SELECT 
    artist, 
    day_of_week,
    hour,
    COUNT(*) as ct
FROM sqlite.songs
WHERE 
    service_id=1 
GROUP BY 
    artist, 
    day_of_week, 
    hour