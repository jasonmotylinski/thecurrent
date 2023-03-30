import config
import json
import musicbrainzngs as mbz 

from dashboard import data
from file_helpers import load_json_data, write_json_data

if __name__ == '__main__':
    mbz.set_useragent('rawk-it.com', '0.1')

    artists=load_json_data(config.MUSICBRAINZ_ARTISTS_JSON)  

    i=0
    for idx,row in data.get_artists().iterrows():
        if row['artist'] not in artists:
            details={}
            if len(row['artist']['artist-list']) > 0:
                details=mbz.search_artists(query=row['artist'])['artist-list'][0]

            artists[row['artist']] = json.dumps({"artist": row["artist"], "data": details})
            i=i+1

            if i==100:
                break
    
    write_json_data(config.MUSICBRAINZ_ARTISTS_JSON, artists)