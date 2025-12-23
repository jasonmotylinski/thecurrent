WITH artist_stats AS (
    SELECT
        artist_lower,
        MAX(artist) AS artist,
        service_id,
        SUM(ct) AS total_plays
    FROM songs_day_of_week_hour
    WHERE
        played_at >= CURRENT_DATE - INTERVAL '90 DAY'
        AND artist_lower IS NOT NULL
        AND artist_lower != ''
    GROUP BY artist_lower, service_id
),
with_station_count AS (
    SELECT
        artist,
        service_id,
        total_plays,
        COUNT(*) OVER (PARTITION BY artist_lower) AS station_count
    FROM artist_stats
)
SELECT
    artist,
    service_id,
    total_plays
FROM with_station_count
WHERE service_id = %(service_id)s
  AND station_count = 1
ORDER BY total_plays DESC
LIMIT 10
