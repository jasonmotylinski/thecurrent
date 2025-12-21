CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_title_trgm
ON songs_day_of_week_hour USING GIN (title gin_trgm_ops);
