CREATE INDEX idx_artists ON songs (
    artist,
    title,
    played_at ASC
);
