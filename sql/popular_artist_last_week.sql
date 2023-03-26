SELECT 
    a.artist, 
    a.title, 
    COUNT(*) as ct
FROM 
    songs a
INNER JOIN
(
    SELECT 
        artist, 
        COUNT(*) as ct
    FROM songs
    WHERE played_at >= '{start_date.year}-{start_date.month:02d}-{start_date.day:02d}T00:00:00.000-06:00'
        AND played_at <= '{end_date.year}-{end_date.month:02d}-{end_date.day:02d}T23:59:59.000-06:00'
    GROUP BY artist
    ORDER BY ct DESC
    LIMIT 10
) AS b
ON a.artist=b.artist
WHERE played_at >= '{start_date.year}-{start_date.month:02d}-{start_date.day:02d}T00:00:00.000-06:00'
        AND played_at <= '{end_date.year}-{end_date.month:02d}-{end_date.day:02d}T23:59:59.000-06:00'
GROUP BY 
    a.artist, 
    a.title

