SELECT 
    a.artist,
    a.title,
    COUNT(*) AS ct
FROM
    songs_day_of_week_hour AS a
INNER JOIN (
    SELECT 
        artist, 
        COUNT(*) as ct
    FROM songs_day_of_week_hour
    WHERE 
        service_id=%(service_id)s
        AND played_at >= CURRENT_DATE - INTERVAL '7 DAY'
        AND played_at <= CURRENT_DATE
    GROUP BY artist
    ORDER BY ct DESC
    LIMIT 10
) AS b ON a.artist = b.artist
WHERE
    a.service_id=%(service_id)s
    AND a.played_at >= CURRENT_DATE - INTERVAL '7 DAY'
    AND a.played_at <= CURRENT_DATE
GROUP BY 
    a.artist, 
    a.title
