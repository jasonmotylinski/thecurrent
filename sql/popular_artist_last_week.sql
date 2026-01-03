SELECT 
    a.artist_normalized,
    a.title_normalized,
    MAX(a.artist) AS artist,
    MAX(a.title) AS title,
    COUNT(*) AS ct
FROM
    songs_day_of_week_hour AS a
INNER JOIN (
    SELECT 
        artist_normalized, 
        COUNT(*) as ct
    FROM songs_day_of_week_hour
    WHERE 
        service_id=%(service_id)s
        AND played_at >= CURRENT_DATE - INTERVAL '7 DAY'
        AND played_at <= CURRENT_DATE
        AND (artist_normalized !='' AND title_normalized !='')
    GROUP BY artist_normalized
    ORDER BY ct DESC
    LIMIT 10
) AS b ON a.artist_normalized = b.artist_normalized
WHERE
    a.service_id=%(service_id)s
    AND a.played_at >= CURRENT_DATE - INTERVAL '7 DAY'
    AND a.played_at <= CURRENT_DATE
GROUP BY 
    a.artist_normalized,
    a.title_normalized