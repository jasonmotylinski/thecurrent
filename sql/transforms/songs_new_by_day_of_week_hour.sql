CREATE OR REPLACE TABLE postgres.songs_new_by_day_of_week_hour AS 
SELECT 
    c.service_id,
    c.day_of_week,
    c.day_of_week_int,
    c.hour,
    CASE WHEN h.ct IS NULL THEN 0 ELSE h.ct END AS ct
FROM ( 
    SELECT service_id, cr.* FROM(VALUES(1),(2),(3),(4),(5),(6),(7), (8), (9)) AS s(service_id)
    RIGHT JOIN(
    SELECT 
        DISTINCT day_of_week, CAST(day_of_week_int AS INT) AS day_of_week_int, CAST(hour AS INT) AS hour
    FROM postgres.calendar
    ) AS cr
    ON 1=1
) AS c
LEFT OUTER JOIN (
    SELECT 
        service_id,
        DAYNAME(played_at) AS day_of_week,
        CAST(HOUR(played_at) AS INT) AS hour,
        COUNT(*) AS ct
    FROM (
        SELECT 
            CAST(service_id AS INT) AS service_id,
            artist, 
            title, 
            CAST(MIN(played_at) AS DATETIME) AS played_at
        FROM sqlite.songs
        WHERE 
            trim(artist) != ''
            AND trim(title) != ''
        GROUP BY
            service_id,
            artist,
            title
        ORDER BY 
            played_at ASC
    )
    WHERE 
        played_at >= CURRENT_DATE - INTERVAL 90 DAY
        AND played_at <= CURRENT_DATE
    GROUP BY 
        service_id,
        DAYNAME(played_at),
        HOUR(played_at)
) AS h
ON 
    c.service_id=h.service_id
    AND c.day_of_week=h.day_of_week
    AND c.hour=h.hour
ORDER BY 
    c.service_id ASC,
    c.day_of_week_int ASC,
    c.hour ASC