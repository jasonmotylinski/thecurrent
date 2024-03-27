WITH week_count(year, week, ct) AS (
    SELECT
        year,
        week,
        COUNT(*) as ct
    FROM 
        songs_day_of_week_hour
    WHERE
        service_id=%(service_id)s
        AND artist='%(artist)s'
        AND title='%(title)s'
        AND played_at >= CURRENT_DATE - INTERVAL '90 DAY'
        AND played_at <= CURRENT_DATE
    GROUP BY
        year,
        week
    ORDER BY
        year ASC,
        week ASC
)

SELECT 
    c.yw,
    CASE WHEN wc.ct IS NULL THEN 0 ELSE wc.ct END AS ct
FROM (
    SELECT 
        DISTINCT
        year,
        week_of_year,
        year || TO_CHAR(week_of_year::int, 'FM00') AS yw
    FROM calendar 
    WHERE
        year != 'year'
) AS c
LEFT OUTER JOIN week_count AS wc ON c.year=wc.year AND c.week_of_year=wc.week
WHERE c.yw >= to_char(CURRENT_DATE - INTERVAL '90 DAY', 'YYYYIW')
AND c.yw < to_char(CURRENT_DATE, 'YYYYIW')
