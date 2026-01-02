WITH top_songs AS (
    SELECT
        MAX(artist) AS artist,
        MAX(title) AS title,
        artist_normalized,
        title_normalized,
        COUNT(*) AS ct
    FROM songs_day_of_week_hour
    WHERE service_id = %(service_id)s
        AND played_at >= CURRENT_DATE - INTERVAL '7 DAY'
        AND played_at <= CURRENT_DATE
        AND artist_normalized != '' AND title_normalized != ''
    GROUP BY artist_normalized, title_normalized
    ORDER BY ct DESC, MAX(artist) ASC
    LIMIT 10
),
weeks AS (
    SELECT DISTINCT
        year,
        week
    FROM songs_day_of_week_hour
    WHERE 
        service_id = %(service_id)s
        AND played_at >= CURRENT_DATE - INTERVAL '90 DAY'
        AND played_at <= CURRENT_DATE
    ORDER BY year, week
)
SELECT
    ts.artist,
    ts.title,
    w.year,
    w.week,
    COALESCE(SUM(s.ct), 0) AS ct
FROM top_songs ts
CROSS JOIN weeks w
LEFT JOIN songs_day_of_week_hour s ON s.artist_normalized = ts.artist_normalized
    AND s.title_normalized = ts.title_normalized
    AND s.year = w.year
    AND s.week = w.week
    AND s.service_id = %(service_id)s
    AND s.played_at >= CURRENT_DATE - INTERVAL '90 DAY'
    AND s.played_at <= CURRENT_DATE
GROUP BY ts.artist, ts.title, w.year, w.week
ORDER BY ts.artist, ts.title, w.year, w.week
