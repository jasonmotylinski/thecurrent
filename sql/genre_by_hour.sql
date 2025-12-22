SELECT
    ag.genre,
    s.hour,
    SUM(s.ct) as plays,
    COUNT(DISTINCT s.service_id) as station_count
FROM songs_day_of_week_hour s
JOIN artist_genres ag ON s.artist = ag.artist
WHERE
    s.played_at >= CURRENT_DATE - INTERVAL '90 DAY'
    AND s.artist != ''
    AND ag.source = 'spotify'
GROUP BY ag.genre, s.hour
HAVING SUM(s.ct) > 100
ORDER BY ag.genre, s.hour
