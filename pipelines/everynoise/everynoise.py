import config
import json
import requests

from bs4 import BeautifulSoup
from file_helpers import load_json_data, write_json_data, load_artists_data

def get_genres(who):
    genres=[]
    r = requests.get(config.EVERYNOISE_URL.format(who=who))

    soup = BeautifulSoup(r.text, "html.parser")

    for s in soup("a",{"title": None}):
        genres.append(s.text)
    
    return genres


if __name__ == '__main__':
    artists = load_artists_data(config.THECURRENT_ARTISTS_CSV)

    artists_genres=load_json_data(config.EVERYNOISE_ARTISTS_GENRES_JSON, "artist")  
    i=0

    for a in artists:
        if a not in artists_genres:
            artists_genres[a] = json.dumps({"artist": a, "genres": get_genres(a)})
            i=i+1

            if i==10:
                break

    write_json_data(config.EVERYNOISE_ARTISTS_GENRES_JSON, artists_genres)