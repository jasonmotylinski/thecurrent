
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
                    LOWER(
                        TRIM(
                            REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                    REGEXP_REPLACE(
                                        REPLACE(artist, ' & ', ' and '),
                                        '\s+(featuring|ft\.?)\s+', ' feat. ', 'gi'
                                    ),
                                    '\s+', ' ', 'g'
                                ),
                                '^\s+|\s+$', '', 'g'
                            )
                        )
                    ) AS artist_normalized,
                    LOWER(title) AS title_normalized,
                    COUNT(*) AS ct
                FROM
                    songs
                WHERE
                    played_at >= DATETIME('now', '-1 year')
                    AND LOWER(artist) != ''
                    AND LOWER(title) != ''
                GROUP BY
                    LOWER(
                        TRIM(
                            REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                    REGEXP_REPLACE(
                                        REPLACE(artist, ' & ', ' and '),
                                        '\s+(featuring|ft\.?)\s+', ' feat. ', 'gi'
                                    ),
                                    '\s+', ' ', 'g'
                                ),
                                '^\s+|\s+$', '', 'g'
                            )
                        )
                    ),
                    LOWER(title)
                ORDER BY
                    ct DESC
                LIMIT 20
            ) s2 ON LOWER(
                TRIM(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                REPLACE(s1.artist, ' & ', ' and '),
                                '\s+(featuring|ft\.?)\s+', ' feat. ', 'gi'
                            ),
                            '\s+', ' ', 'g'
                        ),
                        '^\s+|\s+$', '', 'g'
                    )
                )
            )=s2.artist_normalized AND LOWER(s1.title)=s2.title_normalized
            WHERE
                s1.played_at >= DATETIME('now', '-1 year')
            GROUP BY
                LOWER(
                    TRIM(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                    REPLACE(s1.artist, ' & ', ' and '),
                                    '\s+(featuring|ft\.?)\s+', ' feat. ', 'gi'
                                ),
                                '\s+', ' ', 'g'
                            ),
                            '^\s+|\s+$', '', 'g'
                        )
                    )
                ),
                LOWER(s1.title),
                s1.year,
                s1.week
            ORDER BY
                LOWER(
                    TRIM(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                    REPLACE(s1.artist, ' & ', ' and '),
                                    '\s+(featuring|ft\.?)\s+', ' feat. ', 'gi'
                                ),
                                '\s+', ' ', 'g'
                            ),
                            '^\s+|\s+$', '', 'g'
                        )
                    )
                ) ASC,
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


