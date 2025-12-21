SELECT
    s.artist,
    SUM(s.ct) as total_plays
FROM songs_day_of_week_hour s
WHERE
    s.artist ILIKE '%(search_term)s'
    AND s.artist != ''
GROUP BY s.artist
ORDER BY total_plays DESC
LIMIT 10
