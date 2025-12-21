SELECT
    s.service_id,
    DATE_TRUNC('month', s.played_at) as month,
    COUNT(*) as plays
FROM songs_day_of_week_hour s
WHERE s.artist ILIKE '%(artist)s'
    AND s.artist != ''
GROUP BY s.service_id, DATE_TRUNC('month', s.played_at)
ORDER BY month ASC
