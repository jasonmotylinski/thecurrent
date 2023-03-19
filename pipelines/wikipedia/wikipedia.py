import config
import json
import requests

from bs4 import BeautifulSoup
from file_helpers import load_json_data, write_json_data, load_artists_data


def get_vcard(url):
    r=requests.get(url)
    soup=BeautifulSoup(r.text, "html.parser")
    bio=soup("table", {"class": "vcard"})
    if len(bio) > 0:
        return bio
    return None

if __name__ == '__main__':
    artists_wikipedia=load_json_data(config.ARTISTS_WIKIPEDIA_JSON)
    artists = load_artists_data(config.ARTISTS_CSV)

    i=0
    for artist in artists:    
        if artist not in artists_wikipedia:
            for k in config.WIKIPEDIA_URLS.keys():
                url=config.WIKIPEDIA_URLS[k].format(artist=artist)
                vcard=get_vcard(url)
                if vcard:
                    artists_wikipedia[artist]=json.dumps({"artist": artist,"url": url})
                    break
            
            if not vcard:
                artists_wikipedia[artist]=json.dumps({"artist": artist,"url": ""})
                print("{0} does not have a vcard".format(artist))
            
            i=i+1

            if i==100:
                break
    
    write_json_data(config.ARTISTS_WIKIPEDIA_JSON, artists_wikipedia)
