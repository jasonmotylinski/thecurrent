WITH top_songs AS (
    SELECT
        MAX(artist) AS artist,
        MAX(title) AS title,
        artist_normalized,
        title_normalized,
        SUM(ct) AS total_plays
    FROM songs_day_of_week_hour
    WHERE service_id = %(service_id)s
        AND year = 2025
        AND artist_normalized != ''
        AND title_normalized != ''
    GROUP BY artist_normalized, title_normalized
    ORDER BY total_plays DESC, MAX(artist) ASC
    LIMIT 100
),
months AS (
    SELECT DISTINCT
        DATE_TRUNC('month', played_at) as month
    FROM songs_day_of_week_hour
    WHERE year = 2025
    ORDER BY month
)
SELECT
    ts.artist,
    ts.title,
    m.month,
    COALESCE(SUM(s.ct), 0) AS plays
FROM top_songs ts
CROSS JOIN months m
LEFT JOIN songs_day_of_week_hour s
    ON s.artist_normalized = ts.artist_normalized
    AND s.title_normalized = ts.title_normalized
    AND DATE_TRUNC('month', s.played_at) = m.month
    AND s.service_id = %(service_id)s
    AND s.year = 2025
GROUP BY ts.artist, ts.title, ts.artist_normalized, ts.title_normalized, m.month
ORDER BY ts.artist, ts.title, m.month
