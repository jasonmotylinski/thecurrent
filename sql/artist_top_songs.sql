SELECT
    s.title,
    SUM(s.ct) as total_plays
FROM songs_day_of_week_hour s
WHERE s.artist ILIKE '%(artist)s'
    AND s.title != ''
GROUP BY s.title
ORDER BY total_plays DESC
LIMIT 5
