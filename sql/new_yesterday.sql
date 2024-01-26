SELECT 
    a.artist, 
    a.title, 
    a.played_at
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
    WHERE service_id=1 AND trim(artist) != ''
    or trim(title) != ''
) b
ON a.artist=b.artist
AND a.title=b.title
AND a.played_at=b.played_at
WHERE  b.rank=1
AND b.played_at >= '{yesterday.year}-{yesterday.month:02d}-{yesterday.day:02d}T00:00:00.000-06:00'
AND b.played_at <= '{yesterday.year}-{yesterday.month:02d}-{yesterday.day:02d}T23:59:59.000-06:00'
ORDER BY a.played_at DESC
LIMIT 100