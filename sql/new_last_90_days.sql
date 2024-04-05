
SELECT
    day_of_week,
    day_of_week_int,
    hour,
    ct
FROM
    songs_new_by_day_of_week_hour
WHERE
    service_id=%(service_id)s
ORDER BY
    day_of_week_int ASC,
    hour ASC
