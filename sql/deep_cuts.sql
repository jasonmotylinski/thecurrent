WITH song_stats AS (
    SELECT
        MAX(artist) AS artist,
        MAX(title) AS title,
        artist_lower,
        title_lower,
        COUNT(DISTINCT service_id) as station_count,
        SUM(ct) as total_plays,
        MAX(ct) as max_station_plays
    FROM songs_day_of_week_hour
    WHERE
        played_at >= CURRENT_DATE - INTERVAL '90 DAY'
        AND artist_lower != ''
        AND title_lower != ''
    GROUP BY artist_lower, title_lower
)
SELECT
    artist,
    title,
    station_count,
    total_plays,
    ROUND(total_plays * 1.0 / station_count, 1) as avg_plays_per_station
FROM song_stats
WHERE
    station_count >= 4
    AND total_plays < 100
    AND max_station_plays < 30
ORDER BY station_count DESC, total_plays ASC
LIMIT 10;
