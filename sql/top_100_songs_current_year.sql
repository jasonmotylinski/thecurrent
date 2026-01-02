SELECT
    MAX(artist) AS artist,
    MAX(title) AS title,
    artist_normalized,
    title_normalized,
    SUM(ct) as total_plays
FROM songs_day_of_week_hour
WHERE
    service_id = %(service_id)s
    AND year = 2025
    AND artist_normalized != ''
    AND title_normalized != ''
GROUP BY
    artist_normalized,
    title_normalized
ORDER BY SUM(ct) DESC, MAX(artist) ASC
LIMIT 100
