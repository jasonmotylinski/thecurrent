
SELECT 
    artist, title, ct, rnk
FROM (
SELECT
    artist,
    title,
    COUNT(*) AS ct,
    DENSE_RANK() OVER(
        PARTITION BY artist
        order by COUNT(*) DESC
    ) as rnk
FROM 
    songs
WHERE service_id=1 AND artist != '' and title != ''
GROUP BY
    artist,
    title
ORDER BY
    ct DESC
) 
WHERE
    rnk = 1
