CREATE TABLE artist(
    artist VARCHAR(255),
    spotify_id VARCHAR(50),
    spotify_name VARCHAR(255),
    popularity INTEGER,
    followers INTEGER,
    enriched_at TIMESTAMP
);

-- Create index for efficient lookups
CREATE INDEX idx_artist_spotify_id ON artist(spotify_id);
CREATE INDEX idx_artist_enriched_at ON artist(enriched_at);
