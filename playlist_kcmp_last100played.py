import logging
import json
import pytz
import spotipy
from datetime import datetime
from dotenv import load_dotenv
from pipelines.thecurrent.playlist import get_hour_html, get_songs
from rawkit_playlist import playlist
from spotipy.oauth2 import SpotifyOAuth

PLAYLIST_ID="3PolUEn6bpV7PPQO8EKkAc"

load_dotenv()

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_object = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        return json.dumps(log_object)

# Set up logging with JSON formatter
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# authenticating
scope = "playlist-modify-public user-library-read"
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
# user ID for all user parameters in future functions
user = spotify.current_user()["id"]

def get_timezone_offset():
    timezone_name = 'America/New_York'  
    timezone = pytz.timezone(timezone_name)
    local_time = datetime.now(timezone)
    is_dst = bool(local_time.dst())
    
    logger.info("get_timezone_offset: is_dst: {0}".format(is_dst))
    if is_dst:
        return -1
    else:
        return -1


def get_recent_songs():
    dte=datetime.now()
    year=dte.year
    month=dte.month
    day=dte.day
    hour=dte.hour + get_timezone_offset()

    html=get_hour_html(year, month, day, hour)
    return get_songs(html)

def prune_playlist(pl):
    max_playlist_length=100
    
    if len(pl['tracks']['items']) == max_playlist_length:
        logger.info("prune_playlist: Playlist is at max length. Removing last item")
        spotify.playlist_remove_all_occurrences_of_items(playlist_id=pl['id'], items=[pl['tracks']['items'][max_playlist_length-1]['track']['uri']])

def update_playlist(last100playlist, spotify_details_for_most_recent_played):
    should_add=False

    if len(last100playlist['tracks']['items']) > 0:
        if last100playlist['tracks']['items'][0]['track']['uri'] != spotify_details_for_most_recent_played:
            should_add=True
    else:
        should_add=True

    logger.info("update_playlist: should_add: {0}".format(should_add))
    if should_add:
        prune_playlist(last100playlist)
        logger.info("update_playlist: adding most recent played uri: {0}".format(spotify_details_for_most_recent_played))
        spotify.playlist_add_items(playlist_id=last100playlist['id'],items=[spotify_details_for_most_recent_played],position=0)


if __name__=="__main__": 


    # get the most recent played from The Current's website
    recent_songs=list(get_recent_songs())
    if len(recent_songs) > 0:
        most_recent_played=recent_songs[0]
        logger.info("main: most_recent_played: {0}".format(most_recent_played))

        # Get the spotify details for the most recent played 
        spotify_details_for_most_recent_played=playlist.compile_track_ids([{"artist_name": most_recent_played['artist'], "song_name": most_recent_played["title"]}])[0]

        # Get the last 100 playlist
        last100playlist=spotify.playlist(PLAYLIST_ID)

        # Update the playlist with the details
        update_playlist(last100playlist, spotify_details_for_most_recent_played)
    else:
        logger.error("main: Unable to get_recent_songs. Found 0")

