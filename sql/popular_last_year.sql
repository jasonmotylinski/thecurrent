SELECT 
    artist,
    title,
    year,
    week,
    MAX(ct)
FROM (
    SELECT 
        s1.artist,
        s1.title,
        s1.year,
        s1.week,
        COUNT(*) AS ct
    FROM songs s1
    INNER JOIN (
        SELECT
            artist,
            title,
            COUNT(*) as ct
            FROM 
            songs
        WHERE
            played_at >=  DATETIME('now', '-1 year')
        GROUP BY 
            artist,
            title
        ORDER BY ct DESC
        LIMIT 20
    ) s2 ON s1.artist=s2.artist AND s1.title=s2.title
    WHERE
        played_at >=  DATETIME('now', '-1 year')
    GROUP BY 
        s1.artist, 
        s1.title, 
        s1.year, 
        s1.week
    ORDER BY
        s1.artist ASC, 
        s1.title ASC, 
        s1.year ASC, 
        s1.week ASC, 
        ct DESC
)
GROUP BY
    artist,
    title
ORDER BY year, week ASC