WITH top_songs AS (
    SELECT s2.title, SUM(s2.ct) as total
    FROM songs_day_of_week_hour s2
    WHERE s2.artist ILIKE '%(artist)s' AND s2.title != ''
    GROUP BY s2.title
    ORDER BY total DESC
    LIMIT 5
),
date_range AS (
    SELECT
        MIN(DATE_TRUNC('month', played_at)) as min_month,
        MAX(DATE_TRUNC('month', played_at)) as max_month
    FROM songs_day_of_week_hour
    WHERE artist ILIKE '%(artist)s'
),
months AS (
    SELECT DISTINCT DATE_TRUNC('month', calendar_date::date) as month
    FROM calendar, date_range
    WHERE calendar_date::date >= date_range.min_month
      AND calendar_date::date <= date_range.max_month
),
song_months AS (
    SELECT
        ts.title,
        m.month
    FROM top_songs ts
    CROSS JOIN months m
),
play_counts AS (
    SELECT
        s.title,
        DATE_TRUNC('month', s.played_at) as month,
        COUNT(*) as plays
    FROM songs_day_of_week_hour s
    WHERE s.artist ILIKE '%(artist)s'
      AND s.title IN (SELECT title FROM top_songs)
    GROUP BY s.title, DATE_TRUNC('month', s.played_at)
)

SELECT
    sm.title,
    sm.month,
    COALESCE(pc.plays, 0) as plays
FROM song_months sm
LEFT JOIN play_counts pc ON sm.title = pc.title AND sm.month = pc.month
ORDER BY sm.title, sm.month ASC
