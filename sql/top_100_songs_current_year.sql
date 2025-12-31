SELECT
    MAX(artist) AS artist,
    MAX(title) AS title,
    artist_lower,
    title_lower,
    SUM(ct) as total_plays
FROM songs_day_of_week_hour
WHERE
    service_id = %(service_id)s
    AND EXTRACT(YEAR FROM played_at) = EXTRACT(YEAR FROM CURRENT_DATE)
    AND artist_lower != ''
    AND title_lower != ''
GROUP BY
    artist_lower,
    title_lower
ORDER BY SUM(ct) DESC, MAX(artist) ASC
LIMIT 100
