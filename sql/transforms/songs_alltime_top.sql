CREATE OR REPLACE TABLE postgres.songs_alltime_top AS 
SELECT 
    artist, COUNT(*) as ct 
FROM 
    sqlite.songs
WHERE 
    service_id=1
GROUP BY artist
ORDER BY ct DESC
LIMIT 5