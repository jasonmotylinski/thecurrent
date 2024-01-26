SELECT artist, COUNT(*) as ct 
FROM songs
WHERE service_id=1
GROUP BY artist
ORDER BY ct DESC
LIMIT 5