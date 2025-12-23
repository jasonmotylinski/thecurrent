"""Luigi tasks for inserting Spotify artist data into the database."""
import config
import json
import luigi
import sqlite3
from datetime import datetime, timedelta
from pipelines.spotify.json_tasks import FetchSpotifyArtistsForDay


def get_connection():
    """Get SQLite database connection."""
    return sqlite3.connect(config.DB)


def insert_artist(con, artist, spotify_data):
    """Insert or update artist in the artist table.

    Args:
        con: Database connection
        artist: Artist name
        spotify_data: Spotify API response data (or None)
    """
    # Check if artist already exists
    t = """SELECT artist FROM artist WHERE artist=? LIMIT 1"""
    results = con.execute(t, (artist,)).fetchall()

    if len(results) == 0:
        # Insert new artist with Spotify data
        if spotify_data:
            t = """INSERT INTO artist(artist, spotify_id, spotify_name, popularity, followers, enriched_at)
                   VALUES(?, ?, ?, ?, ?, ?)"""
            con.execute(t, (
                artist,
                spotify_data.get('id'),
                spotify_data.get('name'),
                spotify_data.get('popularity'),
                spotify_data.get('followers', {}).get('total'),
                datetime.utcnow().isoformat()
            ))
        else:
            # Insert artist without Spotify data
            t = "INSERT INTO artist(artist, enriched_at) VALUES(?, ?)"
            con.execute(t, (artist, datetime.utcnow().isoformat()))
        con.commit()


def insert_genres(con, artist, genres, source='spotify'):
    """Insert genres for an artist.

    Args:
        con: Database connection
        artist: Artist name
        genres: List of genre strings
        source: Data source identifier
    """
    for genre in genres:
        t = """SELECT artist, genre, source FROM artist_genres
               WHERE artist=? AND genre=? AND source=? LIMIT 1"""
        results = con.execute(t, (artist, genre, source)).fetchall()

        if len(results) == 0:
            t = "INSERT INTO artist_genres(artist, genre, source) VALUES(?, ?, ?)"
            con.execute(t, (artist, genre, source))
            con.commit()


def insert_images(con, artist, images, source='spotify'):
    """Insert images for an artist.

    Args:
        con: Database connection
        artist: Artist name
        images: List of image dicts with height, width, url
        source: Data source identifier
    """
    for img in images:
        t = """SELECT artist, height, width, url, source FROM artist_images
               WHERE artist=? AND height=? AND width=? AND url=? AND source=? LIMIT 1"""
        results = con.execute(t, (
            artist, img['height'], img['width'], img['url'], source
        )).fetchall()

        if len(results) == 0:
            t = "INSERT INTO artist_images(artist, height, width, url, source) VALUES(?, ?, ?, ?, ?)"
            con.execute(t, (artist, img['height'], img['width'], img['url'], source))
            con.commit()


class InsertSpotifyArtistsToDb(luigi.Task):
    """Insert Spotify artist data from JSON into the database.

    Reads the JSON file produced by FetchSpotifyArtistsForDay and inserts
    the data into artist, artist_genres, and artist_images tables.
    """
    date = luigi.DateParameter()

    def requires(self):
        """Require the JSON fetch task to complete first."""
        return FetchSpotifyArtistsForDay(self.date)

    def output(self):
        """Marker file indicating successful DB insertion."""
        d = self.date
        path = f"output/spotify/artists/markers/{d.year}/{d.month:02d}/{d.strftime('%Y%m%d')}.done"
        return luigi.LocalTarget(path)

    def run(self):
        """Read JSON and insert artists into database."""
        import os

        con = get_connection()
        artists_processed = 0

        # Read line-delimited JSON file
        with self.input().open('r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                artist_entry = json.loads(line)
                artists_processed += 1

                artist = artist_entry['query_artist']
                spotify_data = artist_entry.get('spotify_response')

                # Insert artist
                insert_artist(con, artist, spotify_data)

                # Insert genres and images if we have Spotify data
                if spotify_data:
                    if 'genres' in spotify_data:
                        insert_genres(con, artist, spotify_data['genres'])
                    if 'images' in spotify_data:
                        insert_images(con, artist, spotify_data['images'])

        con.close()

        # Create marker file
        d = os.path.dirname(self.output().path)
        if not os.path.exists(d):
            os.makedirs(d)
        with self.output().open('w') as f:
            f.write(f"Completed: {datetime.utcnow().isoformat()}\n")
            f.write(f"Artists processed: {artists_processed}\n")


class SpotifyArtistsBackfillLastXDays(luigi.WrapperTask):
    """Enrich Spotify artists for the last X days.

    Runs after station data ingestion to enrich newly played artists.
    """
    last_x_days = luigi.IntParameter(default=7)

    def requires(self):
        """Require InsertSpotifyArtistsToDb for each of the last X days."""
        for i in range(1, self.last_x_days + 1):
            yield InsertSpotifyArtistsToDb(datetime.now().date() - timedelta(days=i))
