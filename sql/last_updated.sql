SELECT played_at::date
FROM public.songs_day_of_week_hour
WHERE service_id=1
ORDER BY played_at DESC
LIMIT 1
