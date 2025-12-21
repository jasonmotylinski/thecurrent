SELECT
    s.artist,
    total_plays
FROM artists s
WHERE
    s.artist ILIKE '%(search_term)s'
    AND s.artist != ''
ORDER BY total_plays DESC
LIMIT 10
