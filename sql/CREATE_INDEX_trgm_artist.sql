CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_artist_trgm
ON songs_day_of_week_hour USING GIN (artist gin_trgm_ops);
