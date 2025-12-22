WITH artist_stations AS (
    SELECT
        artist,
        COUNT(DISTINCT service_id) as station_count,
        MAX(service_id) as primary_station,
        SUM(ct) as total_plays
    FROM songs_day_of_week_hour
    WHERE
        played_at >= CURRENT_DATE - INTERVAL '90 DAY'
        AND artist != ''
    GROUP BY artist
)
SELECT
    primary_station as service_id,
    artist,
    total_plays,
    station_count
FROM artist_stations
WHERE
    station_count = 1
    AND primary_station = %(service_id)s
ORDER BY total_plays DESC
LIMIT 10
