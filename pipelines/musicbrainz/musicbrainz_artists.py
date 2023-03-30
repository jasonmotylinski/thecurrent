import config
import json
import musicbrainzngs as mbz 

from dashboard import data
from file_helpers import load_json_data, write_json_data

if __name__ == '__main__':
    mbz.set_useragent('rawk-it.com', '0.1')

    artists=load_json_data(config.MUSICBRAINZ_ARTISTS_JSON, 'artist')  

    i=0
    for idx,row in data.get_artists().iterrows():
        artist=row['artist'].strip()
        if artist not in artists:
            details={}
            results=mbz.search_artists(query=artist)['artist-list']
            if len(results) > 0:
                details=results[0]

            artists[artist] = json.dumps({"artist": artist, "data": details})
            i=i+1

            if i==100:
                break
    
    write_json_data(config.MUSICBRAINZ_ARTISTS_JSON, artists)