"""Luigi tasks for fetching Spotify artist metadata and saving as JSON."""
import config
import json
import luigi
import os
import spotipy
import sqlite3
import time
from datetime import datetime
from spotipy.oauth2 import SpotifyClientCredentials


def get_connection():
    """Get SQLite database connection."""
    return sqlite3.connect(config.DB)


def get_unenriched_artists_for_day(date):
    """Get artists played on a given date that are not yet in the artist table.

    Args:
        date (datetime.date): The date to query

    Returns:
        list: List of (artist, title) tuples
    """
    con = get_connection()
    start_date = datetime.combine(date, datetime.min.time())
    end_date = datetime.combine(date, datetime.max.time())

    query = """
        SELECT DISTINCT s.artist, s.title
        FROM songs s
        LEFT JOIN artist a ON LOWER(s.artist) = LOWER(a.artist)
        WHERE s.artist != ''
          AND s.title != ''
          AND s.played_at >= ?
          AND s.played_at <= ?
          AND a.artist IS NULL
    """
    results = con.execute(query, (start_date.strftime("%Y-%m-%d %H:%M:%S"), end_date.strftime("%Y-%m-%d %H:%M:%S"))).fetchall()
    con.close()
    return results


def get_spotify_client():
    """Create and return a Spotify client with credentials."""
    return spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


def fetch_artist_with_retry(spotify, artist, title, max_retries=3):
    """Fetch artist from Spotify with exponential backoff retry.

    Args:
        spotify: Spotify client
        artist: Artist name
        title: Song title (used to improve search accuracy)
        max_retries: Maximum number of retry attempts

    Returns:
        dict: Spotify artist data or None if not found
    """
    query = f"{artist} {title}"

    for attempt in range(max_retries):
        try:
            results = spotify.search(query, type="track", market="us")
            if results['tracks']['items']:
                artist_uri = results['tracks']['items'][0]['artists'][0]['uri']
                return spotify.artist(artist_uri)
            return None
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:  # Rate limited
                retry_after = int(e.headers.get('Retry-After', 5))
                time.sleep(retry_after)
            elif e.http_status >= 500:  # Server error
                time.sleep(2 ** attempt)
            else:
                raise
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return None
    return None


class FetchSpotifyArtistsForDay(luigi.Task):
    """Fetch Spotify metadata for artists played on a given date.

    Queries for artists that don't yet have Spotify data and fetches
    their metadata from the Spotify API.
    """
    date = luigi.DateParameter()

    def output(self):
        """Output JSON file path for this date."""
        d = self.date
        path = config.SPOTIFY.ARTISTS_JSON_BY_DAY.format(
            year=d.year,
            month=d.month,
            date=d.strftime("%Y%m%d")
        )
        return luigi.LocalTarget(path)

    def run(self):
        """Fetch Spotify data for unenriched artists and save to JSON."""
        # Get unenriched artists for this date
        artists_to_enrich = get_unenriched_artists_for_day(self.date)

        spotify = get_spotify_client()
        artists_data = []
        success_count = 0
        error_count = 0

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

            if spotify_response:
                success_count += 1
            else:
                error_count += 1
                artist_entry["error"] = "No results found"

            artists_data.append(artist_entry)

            # Limit to batch size
            if len(artists_data) >= config.SPOTIFY.BATCH_SIZE:
                break

        # Ensure directory exists
        d = os.path.dirname(self.output().path)
        if not os.path.exists(d):
            os.makedirs(d)

        # Write line-delimited JSON (one artist per line)
        with self.output().open('w') as f:
            for artist_entry in artists_data:
                f.write(json.dumps(artist_entry) + "\n")
