import config
import json

from file_helpers import load_json_data, write_csv_data
from hashlib import sha256


def create_id(artist, title): 
    key = "{0}{1}".format(artist, title)
    m = sha256()
    m.update(key.encode("UTF-8"))
    return m.hexdigest()

if __name__ == '__main__':
    artists_titles=load_json_data(config.MUSICBRAINZ_RELEASEGROUPS_JSON, "artist-title")  
    rows=[]
    rows.append(config.MUSICBRAINZ_RELEASEGROUPS_CSV_HEADER_ROW)
    for k in artists_titles.keys():
        data=json.loads(artists_titles[k])['data']

        if 'first-release-date' in data:
            id=create_id(data['artist-credit-phrase'], data['title'])
            artist=data['artist-credit-phrase']
            title=data['title']
            first_release_date=data['first-release-date']
            rows.append([id, artist, title, first_release_date])

    write_csv_data(config.MUSICBRAINZ_RELEASEGROUPS_CSV, rows)
