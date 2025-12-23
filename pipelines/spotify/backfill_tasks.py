"""Luigi tasks for backfilling Spotify artist data for all unenriched artists."""
import config
import json
import luigi
import os
import time
from datetime import datetime
from pipelines.spotify.json_tasks import fetch_artist_with_retry, get_spotify_client, get_connection
from pipelines.spotify.db_tasks import insert_artist, insert_genres, insert_images


def get_unenriched_artists_all(limit=100):
    """Get all artists not yet in the artist table (for backfill).

    Args:
        limit (int): Maximum number of artists to return

    Returns:
        list: List of (artist, title) tuples
    """
    con = get_connection()
    query = """
        SELECT DISTINCT s.artist, s.title
        FROM songs s
        LEFT JOIN artist a ON LOWER(s.artist) = LOWER(a.artist)
        WHERE s.artist != ''
          AND s.title != ''
          AND a.artist IS NULL
        LIMIT ?
    """
    results = con.execute(query, (limit,)).fetchall()
    con.close()
    return results


class SpotifyArtistsBackfill(luigi.Task):
    """Backfill Spotify metadata for all unenriched artists.

    Unlike the daily task which processes artists by date, this task
    queries for ALL artists that haven't been enriched yet and processes
    them in batches.
    """
    batch_size = luigi.IntParameter(default=100)

    def output(self):
        """Output JSON file with timestamp for this backfill run."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = config.SPOTIFY.ARTISTS_BACKFILL_JSON.format(timestamp=timestamp)
        return luigi.LocalTarget(path)

    def run(self):
        """Fetch Spotify data for all unenriched artists and save to JSON + DB."""
        # Get unenriched artists
        artists_to_enrich = get_unenriched_artists_all(limit=self.batch_size)
        artists_data = []

        if artists_to_enrich:
            spotify = get_spotify_client()
            con = get_connection()

            for artist_row in artists_to_enrich:
                artist = artist_row[0].strip()
                title = artist_row[1].strip()

                # Rate limit delay
                time.sleep(config.SPOTIFY.RATE_LIMIT_DELAY)

                # Fetch from Spotify
                spotify_response = fetch_artist_with_retry(spotify, artist, title)

                artist_entry = {
                    "query_artist": artist,
                    "query_title": title,
                    "spotify_response": spotify_response,
                    "matched": spotify_response is not None,
                    "fetched_at": datetime.utcnow().isoformat()
                }

                if not spotify_response:
                    artist_entry["error"] = "No results found"

                artists_data.append(artist_entry)

                # Insert into database immediately
                insert_artist(con, artist, spotify_response)
                if spotify_response:
                    if 'genres' in spotify_response:
                        insert_genres(con, artist, spotify_response['genres'])
                    if 'images' in spotify_response:
                        insert_images(con, artist, spotify_response['images'])

            con.close()

        # Ensure directory exists
        d = os.path.dirname(self.output().path)
        if not os.path.exists(d):
            os.makedirs(d)

        # Write line-delimited JSON (one artist per line)
        with self.output().open('w') as f:
            for artist_entry in artists_data:
                f.write(json.dumps(artist_entry) + "\n")
