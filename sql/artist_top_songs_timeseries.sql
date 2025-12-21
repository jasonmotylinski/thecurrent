SELECT
    s.title,
    s.service_id,
    DATE_TRUNC('month', s.played_at) as month,
    COUNT(*) as plays
FROM songs_day_of_week_hour s
WHERE s.artist ILIKE '%(artist)s'
    AND s.title IN (
        SELECT title FROM (
            SELECT s2.title, SUM(s2.ct) as total
            FROM songs_day_of_week_hour s2
            WHERE s2.artist ILIKE '%(artist)s' AND s2.title != ''
            GROUP BY s2.title
            ORDER BY total DESC
            LIMIT 5
        ) top_songs
    )
GROUP BY s.title, s.service_id, DATE_TRUNC('month', s.played_at)
ORDER BY s.title, month ASC
