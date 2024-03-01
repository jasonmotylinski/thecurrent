SELECT 
    artist, 
    SUM(ct) AS ct
FROM artists_day_of_week_hour
WHERE 
    day_of_week='%(day_of_week)s'
    AND hour='%(hour)s'
GROUP BY 
    artist,
    day_of_week,
    hour
ORDER BY ct DESC
LIMIT 5