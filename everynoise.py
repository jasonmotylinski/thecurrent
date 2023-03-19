import json
import os
import requests

from bs4 import BeautifulSoup

ARTISTS_CSV="artists.csv"
ARTISTS_GENRES_JSON="artists_genres.json"
EVERYNOISE_URL="https://everynoise.com/lookup.cgi?who={who}&mode=map"

def get_genres(who):
    genres=[]
    r = requests.get(EVERYNOISE_URL.format(who=who))

    soup = BeautifulSoup(r.text)

    for s in soup("a",{"title": None}):
        genres.append(s.text)
    
    return genres

def clean_artist(artist):
    artist=artist.strip()

    if(artist[0]== '"'):
        artist=artist[1:]
        artist=artist[:-1]

    return artist

def load_data():
    artists_genres = {}
    if os.path.exists(ARTISTS_GENRES_JSON):
        with open(ARTISTS_GENRES_JSON,'r') as f:
            for l in f.readlines():
                file_data = json.loads(l)
                artists_genres[file_data["artist"]] = l.strip()
    return artists_genres


with open(ARTISTS_CSV, 'r') as f:
    artists = f.readlines()

artists_genres=load_data()  
i=0

for l in artists:
    a = clean_artist(l)
    if a not in artists_genres:
        artists_genres[a] = json.dumps({"artist": a, "genres": get_genres(a)})
        i=i+1

        if i==100:
            break


with open(ARTISTS_GENRES_JSON, 'w') as f:
    for key in artists_genres.keys():
        f.writelines("{0}\n".format(artists_genres[key]))