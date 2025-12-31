WITH top_songs AS (
    SELECT
        MAX(artist) AS artist,
        MAX(title) AS title,
        artist_lower,
        title_lower,
        SUM(ct) AS total_plays
    FROM songs_day_of_week_hour
    WHERE service_id = %(service_id)s
        AND EXTRACT(YEAR FROM played_at) = EXTRACT(YEAR FROM CURRENT_DATE)
        AND artist_lower != ''
        AND title_lower != ''
    GROUP BY artist_lower, title_lower
    ORDER BY total_plays DESC, MAX(artist) ASC
    LIMIT 100
),
months AS (
    SELECT DISTINCT
        DATE_TRUNC('month', played_at) as month
    FROM songs_day_of_week_hour
    WHERE EXTRACT(YEAR FROM played_at) = EXTRACT(YEAR FROM CURRENT_DATE)
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
    ON s.artist_lower = ts.artist_lower
    AND s.title_lower = ts.title_lower
    AND DATE_TRUNC('month', s.played_at) = m.month
    AND s.service_id = %(service_id)s
    AND EXTRACT(YEAR FROM s.played_at) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY ts.artist, ts.title, ts.artist_lower, ts.title_lower, m.month
ORDER BY ts.artist, ts.title, m.month
