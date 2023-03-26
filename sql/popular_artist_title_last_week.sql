SELECT artist, title, COUNT(*) as ct
FROM songs
WHERE played_at >= '{start_date.year}-{start_date.month:02d}-{start_date.day:02d}T00:00:00.000-06:00'
AND played_at <= '{end_date.year}-{end_date.month:02d}-{end_date.day:02d}T23:59:59.000-06:00'
GROUP BY artist, title
ORDER BY ct DESC
LIMIT 10