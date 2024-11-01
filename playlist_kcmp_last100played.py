import spotipy
from datetime import datetime
from dotenv import load_dotenv
from pipelines.thecurrent.playlist import get_hour_html, get_songs
from rawkit_playlist import playlist
from spotipy.oauth2 import SpotifyClientCredentials

PLAYLIST_ID="3PolUEn6bpV7PPQO8EKkAc"
load_dotenv()

# authenticating
auth_manager = SpotifyClientCredentials()
spotify = spotipy.Spotify(auth_manager=auth_manager)
# user ID for all user parameters in future functions
user = spotify.current_user()["id"]

def get_recent_songs():
    dte=datetime.now()
    year=dte.year
    month=dte.month
    day=dte.day
    hour=dte.hour-1

    html=get_hour_html(year, month, day, hour)
    return get_songs(html)

def prune_playlist(pl):
    max_playlist_length=100
    
    if len(pl['tracks']['items']) == max_playlist_length:
        spotify.playlist_remove_all_occurrences_of_items(playlist_id=pl['id'], items=[pl['tracks']['items'][max_playlist_length-1]['track']['uri']])

def update_playlist(last100playlist, spotify_details_for_most_recent_played):
    should_add=False

    if len(last100playlist['tracks']['items']) > 0:
        if last100playlist['tracks']['items'][0]['track']['uri'] != spotify_details_for_most_recent_played:
            should_add=True
    else:
        should_add=True


    if should_add:
        prune_playlist(last100playlist)
        spotify.playlist_add_items(playlist_id=last100playlist['id'],items=[spotify_details_for_most_recent_played],position=0)


if __name__=="__main__": 
    # get the most recent played from The Current's website
    most_recent_played=list(get_recent_songs())[0]

    # Get the spotify details for the most recent played 
    spotify_details_for_most_recent_played=playlist.compile_track_ids([{"artist_name": most_recent_played['artist'], "song_name": most_recent_played["title"]}])[0]

    # Get the last 100 playlist
    last100playlist=spotify.playlist(PLAYLIST_ID)

    # Update the playlist with the details
    update_playlist(last100playlist, spotify_details_for_most_recent_played)
