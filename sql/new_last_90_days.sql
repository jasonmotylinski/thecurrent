-- Get unique songs in the last 90 days by their first play date
-- Includes all day/hour combinations from calendar, with 0 for days with no new plays
WITH first_plays AS (
    SELECT
        service_id,
        day_of_week,
        day_of_week_int,
        hour,
        played_at,
        ROW_NUMBER() OVER (PARTITION BY service_id, artist, title ORDER BY played_at ASC) as play_order
    FROM songs_day_of_week_hour
    WHERE
        service_id = %(service_id)s
        AND played_at >= CURRENT_DATE - INTERVAL '90 days'
),
new_songs_by_hour AS (
    SELECT
        day_of_week,
        day_of_week_int,
        hour,
        COUNT(*) as ct
    FROM first_plays
    WHERE play_order = 1
    GROUP BY
        day_of_week,
        day_of_week_int,
        hour
),
all_hours AS (
    SELECT
        DISTINCT day_of_week,
        CAST(day_of_week_int AS INT) as day_of_week_int,
        CAST(hour AS INT) as hour
    FROM calendar
)
SELECT
    a.day_of_week,
    a.day_of_week_int,
    a.hour,
    CASE WHEN n.ct IS NULL THEN 0 ELSE n.ct END as ct
FROM all_hours a
LEFT OUTER JOIN new_songs_by_hour n
    ON a.day_of_week = n.day_of_week
    AND a.hour = n.hour
ORDER BY
    a.day_of_week_int ASC,
    a.hour ASC
