SELECT 
    artist,
    title
FROM songs_day_of_week_hour
WHERE
    artist != '' 
    AND title != ''
    AND played_at >= '%(start_date)s'
    AND played_at <= '%(end_date)s'
GROUP BY 
    artist,
    title