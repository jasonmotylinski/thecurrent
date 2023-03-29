WITH week_count(ymw, ct) AS (
    SELECT 
        CAST(year || PRINTF('%02d',month) ||  PRINTF('%02d',week) AS INT) AS ymw,
        COUNT(*) as ct
    FROM 
        songs
    WHERE  
        artist="{artist}"
        AND title="{title}"
        AND played_at >= '{start_date.year}-{start_date.month:02d}-{start_date.day:02d}T00:00:00.000-06:00'
        AND played_at <= '{end_date.year}-{end_date.month:02d}-{end_date.day:02d}T23:59:59.000-06:00'
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
DISTINCT CAST(year || PRINTF('%02d',month) ||  PRINTF('%02d',week_of_year) AS INT) AS ymw 
    FROM calendar 
) c
LEFT OUTER JOIN week_count wc ON c.ymw=wc.ymw
WHERE c.ymw >= '{start_date.year}{start_date.month:02d}{start_date_week:02d}'
AND c.ymw <= '{end_date.year}{end_date.month:02d}{end_date_week:02d}'
