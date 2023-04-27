import config
import json

from datetime import datetime
from file_helpers import load_json_data, write_csv_data
from hashlib import sha256


def create_id(artist, title): 
    key = "{0}{1}".format(artist, title)
    m = sha256()
    m.update(key.encode("UTF-8"))
    return m.hexdigest()

if __name__ == '__main__':
    artists_titles=load_json_data(config.MUSICBRAINZ_RECORDINGS_JSON, "artist-title")  
    rows=[]
    rows.append(config.MUSICBRAINZ_RECORDINGS_CSV_HEADER_ROW)
    for k in artists_titles.keys():
        data=json.loads(artists_titles[k])['data']

        if 'title' in data:
            oldest=datetime.now().strftime("%Y-%m-%d")
            title=data['title']
            artist=data['artist-credit-phrase']
            id=create_id(artist, title)
            for release in data['release-list']:
                if 'release-event-list' in release:
                    for event in release['release-event-list']:
                        if 'US' in event['area']['iso-3166-1-code-list']:
                            if event['date'] < oldest:
                                oldest=event['date']
        
            rows.append([id, artist, title, oldest])

    write_csv_data(config.MUSICBRAINZ_RECORDINGS_CSV, rows)
