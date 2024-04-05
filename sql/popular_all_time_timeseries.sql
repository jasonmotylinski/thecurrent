SELECT 
    artist, 
    CAST(year AS INT) AS year,
    CAST(month AS INT) AS month,
    year || '-' || month AS year_month, 
    COUNT(*) as ct 
FROM songs_day_of_week_hour
WHERE artist IN(
    SELECT artist
    FROM songs_day_of_week_hour
    WHERE 
        service_id=%(service_id)s
        AND artist != ''
        AND title != ''
    GROUP BY artist
    ORDER BY COUNT(*) DESC
    LIMIT 5
)
AND service_id=%(service_id)s
GROUP BY artist, year, month
ORDER BY year ASC, month ASC