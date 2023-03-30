import config
import json
import musicbrainzngs as mbz 

from dashboard import data
from file_helpers import load_json_data, write_json_data

if __name__ == '__main__':
    mbz.set_useragent('rawk-it.com', '0.1')

    releasegroups=load_json_data(config.MUSICBRAINZ_RELEASEGROUPS_JSON,'artist-title')  

    i=0
    for idx,row in data.get_artists_titles().iterrows():
        key=row["artist"].strip()+"-"+row['title'].strip()
        if key not in releasegroups:
            details={}
            results=mbz.search_release_groups(artist=row['artist'], release=row['title'])['release-group-list']
            if len(results) > 0:
                details=results[0]

            releasegroups[key] = json.dumps({"artist-title": key, "data": details})
            i=i+1

            if i==100:
                break
    
    write_json_data(config.MUSICBRAINZ_RELEASEGROUPS_JSON, releasegroups)