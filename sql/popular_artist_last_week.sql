
SELECT 
    a.artist,
    a.title,
    COUNT(*) AS ct
FROM
    songs_day_of_week_hour AS a
WHERE
    a.service_id=%(service_id)s
    AND a.played_at >= CURRENT_DATE - INTERVAL '7 DAY'
    AND a.played_at <= CURRENT_DATE
GROUP BY 
    a.artist, 
    a.title
ORDER BY
    ct DESC
    artist ASC
LIMIT 10