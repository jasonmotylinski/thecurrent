
SELECT
    MAX(artist) AS artist,
    MAX(title) AS title,
    artist_normalized,
    title_normalized,
    COUNT(*) as ct
FROM songs_day_of_week_hour
WHERE
    service_id=%(service_id)s
    AND played_at >= CURRENT_DATE - INTERVAL '7 DAY'
    AND played_at <= CURRENT_DATE
    AND artist_normalized != '' AND title_normalized != ''
GROUP BY
    artist_normalized,
    title_normalized
ORDER BY ct DESC, artist ASC
LIMIT 10
