WITH week_count(year, month, week, ct) AS (
    SELECT
        year,
        month,
        week,
        COUNT(*) as ct
    FROM 
        songs_day_of_week_hour
    WHERE  
        artist='{artist}'
        AND title='{title}'
        AND played_at >= CURRENT_DATE - INTERVAL '90 DAY'
        AND played_at <= CURRENT_DATE
    GROUP BY
        year,
        month,
        week
    ORDER BY
        year ASC,
        month ASC,
        week ASC
)

SELECT 
    c.ymw,
    CASE WHEN wc.ct IS NULL THEN 0 ELSE wc.ct END AS ct
FROM (
    SELECT 
        DISTINCT
        year,
        month,
        week_of_year,
        year || TO_CHAR(month::int, 'FM00') || TO_CHAR(week_of_year::int, 'FM00') AS ymw
    FROM calendar 
    WHERE
        month != 'month'
) AS c
LEFT OUTER JOIN week_count AS wc ON c.year=wc.year AND c.month=wc.month AND c.week_of_year=wc.week
WHERE c.ymw >= to_char(CURRENT_DATE - INTERVAL '90 DAY', 'YYYYMMIW')
AND c.ymw <= to_char(CURRENT_DATE, 'YYYYMMIW')
