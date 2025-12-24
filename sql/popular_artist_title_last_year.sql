
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
                    MAX(artist) AS artist,
                    MAX(title) AS title,
                    LOWER(artist) AS artist_lower,
                    LOWER(title) AS title_lower,
                    COUNT(*) AS ct
                FROM 
                    songs
                WHERE 
                    played_at >= DATETIME('now', '-1 year')
                    AND LOWER(artist) != ''
                    AND LOWER(title) != ''
                GROUP BY
                    LOWER(artist),
                    LOWER(title)
                ORDER BY
                    ct DESC
                LIMIT 20
            ) s2 ON LOWER(s1.artist)=s2.artist_lower AND LOWER(s1.title)=s2.title_lower
            WHERE
                s1.played_at >= DATETIME('now', '-1 year')
            GROUP BY    
                LOWER(s1.artist),
                LOWER(s1.title),
                s1.year,
                s1.week
            ORDER BY
                LOWER(s1.artist) ASC,
                LOWER(s1.title) ASC,
                ct DESC
        )
    )
    WHERE rnk=1
    ORDER BY year_week ASC
) a ON c.year = a.year AND c.week_of_year = a.week
WHERE
calendar_date >= date('now', '-1 year')
AND calendar_date < date('now')


