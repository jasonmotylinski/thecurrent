CREATE OR REPLACE TABLE postgres.songs_day_of_week_hour AS 
SELECT 
    CAST(service_id AS INT) as service_id,
    artist, 
    title,
    CAST(played_at AS DATE) as played_at,
    CAST(year AS INT) as year,
    CAST(month AS INT) as month,
    CAST(week AS INT) as week,
    day_of_week,
    CAST(hour AS INT) as hour,
    COUNT(*) as ct
FROM sqlite.songs

GROUP BY 
    service_id,
    artist, 
    title,
    CAST(played_at AS DATE),
    year,
    month,
    week,
    day_of_week, 
    hour