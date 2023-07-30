import config
import json
import spotipy
from dashboard import data
from spotipy.oauth2 import SpotifyClientCredentials
from file_helpers import load_json_data, write_json_data

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

artists=load_json_data(config.SPOTIFY_ARTISTS_JSON, 'artist')  

if __name__ == '__main__':
    i=0
    for idx,row in data.get_popular_title_for_each_artist().iterrows():
        artist=row['artist'].strip()
        if artist not in artists:
            details={}
            q=artist + " " + row['title'].strip()
            print("querying: " + q)
            results=spotify.search(q, type="track", market="us")
            if len(results['tracks']['items']) > 0:
                details=spotify.artist(results['tracks']['items'][0]['artists'][0]['uri'])

            artists[artist] = json.dumps({"artist": artist, "data": details})
            i=i+1

            if i==1000:
                break
        
        write_json_data(config.SPOTIFY_ARTISTS_JSON, artists)