import config
import json

from file_helpers import load_json_data, write_csv_data

if __name__ == '__main__':
    artists_genres=load_json_data(config.EVERYNOISE_ARTISTS_GENRES_JSON)  
    rows=[]
    rows.append(config.EVERYNOISE_CSV_HEADER_ROW)
    for k in artists_genres.keys():
        for g in json.loads(artists_genres[k])['genres']:
           rows.append([k.strip(), g.strip(), "everynoise"])
    write_csv_data(config.EVERYNOISE_ARTISTS_GENRES_CSV, rows)
