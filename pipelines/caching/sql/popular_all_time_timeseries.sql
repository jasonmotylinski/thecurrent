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
    GROUP BY artist
    ORDER BY COUNT(*) DESC
    LIMIT 5
)
GROUP BY artist, year, month
ORDER BY year, month ASC