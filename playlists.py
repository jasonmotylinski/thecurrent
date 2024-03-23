import json
from dashboard import data
from rawkit_playlist import playlist

def update_popular_artist_title_last_week_playlist():
    artist_titles = json.loads(data.get_popular_artist_title_last_week().to_json(orient='table'))['data']
    playlist_data=[{"artist_name": at['artist'], "song_name": at['title']} for at in artist_titles]
    playlist.update_playlist("Rawk-it - KCRW - Weekly Top 10", "", playlist_data)


if __name__=="__main__": 
    update_popular_artist_title_last_week_playlist()