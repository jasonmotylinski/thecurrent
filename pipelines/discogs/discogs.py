import config
import json

from file_helpers import load_json_data, write_json_data, load_artists_data

if __name__ == '__main__':
    artists = load_artists_data(config.THECURRENT_ARTISTS_CSV)

    artists_genres=load_json_data(config.EVERYNOISE_ARTISTS_GENRES_JSON)  
    i=0

    for a in artists:
        if a not in artists_genres:
            artists_genres[a] = json.dumps({"artist": a, "genres": get_genres(a)})
            i=i+1

            if i==10:
                break

    write_json_data(config.EVERYNOISE_ARTISTS_GENRES_JSON, artists_genres)