CREATE INDEX idx_artists ON songs (
    service_id,
    artist,
    title,
    played_at ASC
);
