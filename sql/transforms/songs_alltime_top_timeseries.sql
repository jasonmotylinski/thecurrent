CREATE OR REPLACE TABLE postgres.songs_alltime_top_timeseries AS 
SELECT 
    artist, 
    year,
    month,
    year || '-' || month AS year_month, 
    COUNT(*) as ct 
FROM sqlite.songs 
WHERE artist IN(
    SELECT artist
    FROM sqlite.songs
    WHERE service_id=1 
    GROUP BY artist
    ORDER BY COUNT(*) DESC
    LIMIT 5
)
AND service_id=1
GROUP BY artist, year, month
ORDER BY year, month ASC