CREATE OR REPLACE TABLE postgres.calendar AS
SELECT 
    CAST(year AS INT) AS year,
    CAST(month AS INT) AS month,
    CAST(day AS INT) AS day,
    CAST(hour AS INT) AS hour,
    day_of_week,
    CAST(day_of_week_int AS INT) AS day_of_week_int,
    CAST(week_of_year AS INT) AS week_of_year,
    calendar_date
FROM   
    sqlite.calendar
