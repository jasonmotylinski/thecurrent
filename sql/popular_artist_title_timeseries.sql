WITH top_songs AS (
    SELECT MAX(artist) AS artist, MAX(title) AS title, artist_lower, title_lower
    FROM songs_day_of_week_hour
    WHERE service_id = %(service_id)s
        AND played_at >= CURRENT_DATE - INTERVAL '7 DAY'
        AND played_at <= CURRENT_DATE
        AND artist_lower != '' AND title_lower != ''
    GROUP BY artist_lower, title_lower
    ORDER BY SUM(ct) DESC
    LIMIT 10
),
weeks AS (
    SELECT DISTINCT
        EXTRACT(YEAR FROM played_at) AS year,
        EXTRACT(WEEK FROM played_at) AS week
    FROM songs_day_of_week_hour
    WHERE played_at >= CURRENT_DATE - INTERVAL '90 DAY'
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
LEFT JOIN songs_day_of_week_hour s ON s.artist_lower = ts.artist_lower
    AND s.title_lower = ts.title_lower
    AND s.year = w.year
    AND s.week = w.week
    AND s.service_id = %(service_id)s
    AND s.played_at >= CURRENT_DATE - INTERVAL '90 DAY'
    AND s.played_at <= CURRENT_DATE
GROUP BY ts.artist, ts.title, w.year, w.week
ORDER BY ts.artist, ts.title, w.year, w.week
