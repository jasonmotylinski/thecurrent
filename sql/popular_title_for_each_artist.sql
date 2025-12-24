SELECT 
    artist, title, ct, rnk
FROM (
SELECT
    MAX(artist) AS artist,
    MAX(title) AS title,
    COUNT(*) AS ct,
    DENSE_RANK() OVER(
        PARTITION BY LOWER(artist)
        order by COUNT(*) DESC
    ) as rnk
FROM 
    songs
WHERE service_id=1 AND LOWER(artist) != '' and LOWER(title) != ''
GROUP BY
    LOWER(artist),
    LOWER(title)
ORDER BY
    ct DESC
) 
WHERE
    rnk = 1
