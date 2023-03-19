import os
import json

def clean_artist(artist):
    artist=artist.strip()

    if(artist[0]== '"'):
        artist=artist[1:]
        artist=artist[:-1]

    return artist

def load_artists_data(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    artists = []
    for l in lines:
        artists.append(clean_artist(l))
    return artists

def load_json_data(path):
    artists_wikipedia = {}
    if os.path.exists(path):
        with open(path,'r') as f:
            for l in f.readlines():
                file_data = json.loads(l)
                artists_wikipedia[file_data["artist"]] = l.strip()
    return artists_wikipedia

def write_json_data(path, dict):
    dir_path=path.replace(os.path.basename(path),"")
    os.makedirs(dir_path, exist_ok=True)
    with open(path, 'w') as f:
        for key in dict.keys():
            f.writelines("{0}\n".format(dict[key]))
