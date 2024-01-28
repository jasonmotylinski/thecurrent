
WITH new_songs_by_day_of_week_hour(day_of_week, hour, ct) AS (
    SELECT 
        a.day_of_week,
        a.hour,
        COUNT(*) AS ct
    FROM songs a
    INNER JOIN (
        SELECT 
            artist, 
            title, 
            MIN(played_at) AS played_at
        FROM songs
        WHERE 
            service_id = 1 
            AND trim(artist) != ''
            AND trim(title) != ''
        GROUP BY
            artist,
            title
    ) b
    ON 
        a.artist=b.artist
        AND a.title=b.title
        AND a.played_at=b.played_at
    WHERE  
        b.played_at >= Date('now', '-90 days')
        AND a.played_at >= Date('now', '-90 days')
        AND b.played_at <= Date('now')
        AND a.played_at <= Date('now')
    GROUP BY 
        a.day_of_week,
        a.hour
    ORDER BY 
        a.played_at ASC
    LIMIT 1000
)
SELECT 
    c.day_of_week,
    c.day_of_week_int,
    c.hour,
    CASE WHEN h.ct IS NULL THEN 0 ELSE h.ct END AS ct
FROM (
    SELECT 
        DISTINCT day_of_week, day_of_week_int, hour
    FROM calendar 
) AS c
LEFT OUTER JOIN new_songs_by_day_of_week_hour h
ON 
    c.day_of_week=h.day_of_week
    AND c.hour=h.hour
ORDER BY 
    c.day_of_week_int ASC,
   c.hour ASC