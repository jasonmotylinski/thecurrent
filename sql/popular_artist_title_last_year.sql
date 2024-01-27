
SELECT
    DISTINCT
    c.year,
    c.week_of_year,
    c.year || c.week_of_year AS year_week,
    a.artist,
    a.title,
    a.ct
FROM calendar c
LEFT OUTER JOIN
(
    SELECT
    artist,
    title,
    year,
    week,
    year || week AS year_week,
    ct
    FROM (
        SELECT
            artist, 
            title, 
            year, 
            week, 
            ct,
            DENSE_RANK() OVER(PARTITION BY artist, title ORDER BY ct DESC) AS rnk
        FROM (
            SELECT 
                s1.artist,
                s1.title,
                s1.year,
                s1.week,
                COUNT(*) AS ct
            FROM songs s1
            INNER JOIN
            (
                SELECT 
                    artist,
                    title,
                    COUNT(*) AS ct
                FROM 
                    songs
                WHERE 
                    played_at >= DATETIME('now', '-1 year')
                    AND artist != ''
                    AND title != ''
                GROUP BY
                    artist,
                    title
                ORDER BY
                    ct DESC
                LIMIT 20
            ) s2 ON s1.artist=s2.artist AND s1.title=s2.title
            WHERE
                s1.played_at >= DATETIME('now', '-1 year')
            GROUP BY    
                s1.artist,
                s1.title,
                s1.year,
                s1.week
            ORDER BY
                s1.artist ASC,
                s1.title ASC,
                ct DESC
        )
    )
    WHERE rnk=1
    ORDER BY year_week ASC
) a ON c.year = a.year AND c.week_of_year = a.week
WHERE
calendar_date >= date('now', '-1 year')
AND calendar_date < date('now')


