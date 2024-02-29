SELECT 
    artist, 
    ct
FROM artists_day_of_week_hour
WHERE 
    day_of_week='{day_of_week}'
    AND hour='{hour}'
ORDER BY ct DESC
LIMIT 5