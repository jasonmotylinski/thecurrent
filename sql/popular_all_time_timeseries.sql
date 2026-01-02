SELECT
    MAX(artist) AS artist,
    CAST(year AS INT) AS year,
    CAST(month AS INT) AS month,
    year || '-' || month AS year_month,
    COUNT(*) as ct
FROM songs_day_of_week_hour
WHERE artist_normalized IN(
    SELECT artist_normalized
    FROM songs_day_of_week_hour
    WHERE
        service_id=%(service_id)s
        AND artist_normalized != ''
        AND title_normalized != ''
    GROUP BY artist_normalized
    ORDER BY COUNT(*) DESC
    LIMIT 5
)
AND service_id=%(service_id)s
GROUP BY artist_normalized, year, month
ORDER BY year ASC, month ASC