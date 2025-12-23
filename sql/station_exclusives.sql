SELECT 
	t1.artist,
	t1.service_id,
	COUNT(*) AS total_plays
FROM
	songs_day_of_week_hour t1
INNER JOIN
(
	SELECT 
		artist
	FROM
	(
		SELECT 
			lower(artist) AS artist, 
			service_id,
			COUNT(*) AS ct
		FROM public.songs_day_of_week_hour
		WHERE 
			played_at >= CURRENT_DATE - INTERVAL '90 DAY'
			AND artist != ''
		GROUP BY 
			artist, 
			service_id
	) AS b1
	GROUP BY artist
	HAVING COUNT(*) = 1
) t2 ON lower(t1.artist) = lower(t2.artist)
WHERE
    t1.played_at >= CURRENT_DATE - INTERVAL '90 DAY'
	AND t1.service_id = %(service_id)s
GROUP BY 
	t1.artist,
	t1.service_id
ORDER BY total_plays DESC
LIMIT 10