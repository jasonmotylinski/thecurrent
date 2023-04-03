import config
import json
import musicbrainzngs as mbz 

from dashboard import data
from file_helpers import load_json_data, write_json_data

if __name__ == '__main__':
    mbz.set_useragent('rawk-it.com', '0.1')

    recordings=load_json_data(config.MUSICBRAINZ_RECORDINGS_JSON,'artist-title')  

    i=0
    for idx,row in data.get_artists_titles_with_no_release_date().iterrows():
        key=row["artist"].strip()+"-"+row['title'].strip()
        if key not in recordings:
            details={}
            results=mbz.search_recordings(query="artist:{0} AND recording:\"{1}\" AND country:US AND status:Official".format(row["artist"], row["title"]))['recording-list']
            if len(results) > 0:
                details=results[0]

            recordings[key] = json.dumps({"artist-title": key, "data": details})
            i=i+1

            if i==100:
                break
    
    write_json_data(config.MUSICBRAINZ_RECORDINGS_JSON, recordings)