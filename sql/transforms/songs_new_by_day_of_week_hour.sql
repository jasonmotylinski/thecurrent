
CREATE OR REPLACE TABLE postgres.songs_new_by_day_of_week_hour AS 
SELECT 
    c.day_of_week,
    c.day_of_week_int,
    c.hour,
    CASE WHEN h.ct IS NULL THEN 0 ELSE h.ct END AS ct
FROM (
    SELECT 
        DISTINCT day_of_week, day_of_week_int, CAST(hour AS VARCHAR) AS hour
    FROM postgres.calendar 
) AS c
LEFT OUTER JOIN (
    SELECT 
        DAYNAME(played_at) AS day_of_week,
        CAST(HOUR(played_at) AS VARCHAR) AS hour,
        COUNT(*) AS ct
    FROM (
        SELECT 
            artist, 
            title, 
            CAST(MIN(played_at) AS DATETIME) AS played_at
        FROM sqlite.songs
        WHERE 
            service_id = 1 
            AND trim(artist) != ''
            AND trim(title) != ''
        GROUP BY
            artist,
            title
        ORDER BY 
            played_at ASC
    )
    WHERE 
        played_at >= CURRENT_DATE - INTERVAL 90 DAY
        AND played_at <= CURRENT_DATE
    GROUP BY 
        DAYNAME(played_at),
        HOUR(played_at)
) AS h
ON 
    c.day_of_week=h.day_of_week
    AND c.hour=h.hour
ORDER BY 
    c.day_of_week_int ASC,
    c.hour ASC