import json
import spotipy
import spotipy.util as util

USERNAME = '12140608440'
SCOPE = 'playlist-modify-public'
token = util.prompt_for_user_token(USERNAME, SCOPE)

sp = spotipy.Spotify(auth=token)

def get_artist(artist):
    results = sp.search(q='artist:' + artist, type='artist', limit=1)
    return results

def get_track(artist, track):
    results = sp.search(q='track:' + track + ' artist:' + artist, type='track', limit=1)
    return results

def get_playlist(user, playlist_id):
    results = sp.user_playlist(user, playlist_id)
    return results

def get_playlist_tracks(user, playlist_id):
    results = sp.user_playlist_tracks(user, playlist_id)
    return results

def add_tracks(user, playlist_id, track_uris, position=None):
    sp.user_playlist_add_tracks(user, playlist_id, track_uris, position=position)

def replace_tracks(user, playlist_id, track_uris):
    sp.user_playlist_replace_tracks(user, playlist_id, track_uris)

def remove_tracks(user, playlist_id, track_positions):
    sp.user_playlist_remove_specific_occurrences_of_tracks(user, playlist_id, track_positions)
