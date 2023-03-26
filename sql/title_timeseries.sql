SELECT 
    year || month || week  AS ymw,
    COUNT(*) as ct
FROM 
    songs
WHERE  
    artist='{artist}'
    AND title='{title}'
    AND played_at >= '{start_date.year}-{start_date.month:02d}-{start_date.day:02d}T00:00:00.000-06:00'
    AND played_at <= '{end_date.year}-{end_date.month:02d}-{end_date.day:02d}T23:59:59.000-06:00'
GROUP BY
    year,
    month,
    week
ORDER BY
    year ASC,
    month ASC,
    week ASC