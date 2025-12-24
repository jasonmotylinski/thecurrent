SELECT
    ag.genre,
    s.hour,
    SUM(s.ct) as plays
FROM songs_day_of_week_hour s
JOIN artist_genres ag ON s.artist = ag.artist
WHERE
    s.played_at >= CURRENT_DATE - INTERVAL '90 DAY'
    AND s.artist != ''
    AND ag.source = 'spotify'
    AND s.service_id = %(service_id)s
GROUP BY ag.genre, s.hour
HAVING SUM(s.ct) > 10
ORDER BY ag.genre, s.hour
