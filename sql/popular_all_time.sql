SELECT 
    artist, 
    COUNT(*) AS ct 
FROM songs_day_of_week_hour
WHERE 
    service_id=%(service_id)s
    AND artist != ''
    AND title != ''
GROUP BY
    service_id,
    artist
ORDER BY ct DESC
LIMIT 5
