SELECT 
    artist, 
    year,
    month,
    year || "-" || month AS year_month, 
    COUNT(*) as ct 
FROM songs 
WHERE artist IN(
    SELECT artist
    FROM songs
    WHERE service_id=1 
    GROUP BY artist
    ORDER BY COUNT(*) DESC
    LIMIT 5
)
AND service_id=1
GROUP BY artist, year, month
ORDER BY year, month ASC