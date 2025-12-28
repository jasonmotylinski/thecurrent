-- Get unique songs in the last 90 days by their first play date
-- Uses row_number to identify first occurrence of each artist/title/service_id combo
WITH first_plays AS (
    SELECT
        day_of_week,
        day_of_week_int,
        hour,
        ROW_NUMBER() OVER (PARTITION BY service_id, artist, title ORDER BY played_at ASC) as play_order
    FROM songs_day_of_week_hour
    WHERE
        service_id = %(service_id)s
        AND played_at >= CURRENT_DATE - INTERVAL '90 days'
)
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
ORDER BY
    day_of_week_int ASC,
    hour ASC
