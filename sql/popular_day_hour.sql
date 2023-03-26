SELECT 
    artist, 
    COUNT(*) as ct
FROM songs
WHERE day_of_week='{day_of_week}'
    AND hour={hour}
    AND artist != ''
GROUP BY artist
ORDER BY ct DESC
LIMIT 5