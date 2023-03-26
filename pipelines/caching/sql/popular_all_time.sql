SELECT artist, COUNT(*) as ct 
FROM songs
GROUP BY artist
ORDER BY ct DESC
LIMIT 5