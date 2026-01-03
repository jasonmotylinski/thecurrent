SELECT 
    artist_normalized,
    MAX(artist) AS artist,
    COUNT(*) AS ct 
FROM songs_day_of_week_hour
WHERE 
    service_id=%(service_id)s
    AND artist_normalized != ''
    AND title_normalized != ''
GROUP BY
    service_id,
    artist_normalized
ORDER BY ct DESC
LIMIT 5
