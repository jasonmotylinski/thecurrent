SELECT artist, title,
       plays_here,
       plays_elsewhere
FROM (
    SELECT
           MAX(artist) AS artist,
           MAX(title) AS title,
           artist_normalized,
           title_normalized,
           SUM(CASE WHEN service_id = %(service_id)s THEN ct ELSE 0 END) as plays_here,
           SUM(CASE WHEN service_id != %(service_id)s THEN ct ELSE 0 END) as plays_elsewhere
    FROM songs_day_of_week_hour
    WHERE played_at >= CURRENT_DATE - INTERVAL '90 DAY'
      AND artist_normalized != ''
      AND title_normalized != ''
    GROUP BY artist_normalized, title_normalized
) sub
WHERE plays_here >= 3
  AND plays_elsewhere < 20
ORDER BY plays_here DESC, plays_elsewhere ASC
LIMIT 10
