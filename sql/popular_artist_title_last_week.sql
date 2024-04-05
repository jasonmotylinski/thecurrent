SELECT 
    artist, 
    title, 
    SUM(ct) as ct
FROM songs_day_of_week_hour
WHERE
    service_id=%(service_id)s
    AND played_at >= CURRENT_DATE - INTERVAL '7 DAY'
    AND played_at <= CURRENT_DATE
    AND (artist !='' AND title !='')
GROUP BY 
    artist, 
    title
ORDER BY SUM(ct) DESC, artist ASC
LIMIT 10;