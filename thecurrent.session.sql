SELECT 
    artist,
    COUNT(*) AS total 
FROM songs 
WHERE 
    played_at  >= date('now', "-8 weeks") 
    AND played_at <= date('now', "-1 week") 
GROUP BY artist 
HAVING COUNT(*) > 1 
ORDER BY total DESC 
LIMIT 5 
;
select date('now', "-7 days") 