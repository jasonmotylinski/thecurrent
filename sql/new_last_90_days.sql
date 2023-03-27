SELECT 
    a.artist, 
    a.title, 
    a.played_at,
    a.day_of_week,
    a.hour
FROM songs a
INNER JOIN (
    SELECT 
        artist, 
        title, 
        played_at, 
        DENSE_RANK() OVER (
        PARTITION BY artist, title
        ORDER BY played_at ASC) AS rank
    FROM songs
    WHERE trim(artist) != ''
    AND trim(title) != ''
) b
ON 
    a.artist=b.artist
    AND a.title=b.title
    AND a.played_at=b.played_at
WHERE  
    b.rank=1
    AND b.played_at >= '2022-10-01T00:00:00.000-06:00'
    AND b.played_at <= '2022-12-31T23:59:59.000-06:00'
ORDER BY 
    a.played_at DESC
LIMIT 1000