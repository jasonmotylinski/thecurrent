import config
import logging
import requests

from bs4 import BeautifulSoup
from dateutil import parser
from hashlib import sha256



def create_id(played_at, artist, title): 
    key = "{0}{1}{2}".format(played_at, artist, title)
    m = sha256()
    m.update(key.encode("UTF-8"))
    return m.hexdigest()

def get_songs(html):
    """Get the articles for a given year, month, day, hour."""
    bs=BeautifulSoup(html, "html.parser")
    data=bs.find_all("li", {"class": "playlist-card"})
    dt=bs.find("input", {"name": "playlistDate"}).attrs['value']

    for c in data:
        artist_album = c.find_all("div", {"class": "playlist-artist"})
        artist = ''
        if len(artist_album) > 0:
             artist = artist_album[0].text
        album = ''
        if len(artist_album) == 2:
            album = artist_album[1].text

        playlist_time = c.find("div", {"class": "playlist-time"}).text
        playlist_datetime = parser.parse(dt + " " + playlist_time + " -5:00")
        item = {
            "title": c.find("h4").text,
            "artist": artist,
            "album":  album,
            "played_at": playlist_datetime.isoformat()
        }
        
        item["id"] = create_id(item['played_at'], item['artist'], item['title'])
        item["played_at_dt"] = playlist_datetime
        yield(item)

def get_hour_html(year:int, month:int, day:int, hour:int):
    url=config.THECURRENT_HOUR_URL.format(year=year, month=month, day=day, hour=hour)
    logging.info("get_hour_html: url: {0}".format(url))
    r=requests.get(url)
    return r.text


def get_day_html(year:int, month:int, day:int):
    url=config.THECURRENT_DAY_URL.format(year=year, month=month, day=day)
    logging.info("get_day_html: url: {0}".format(url))
    r=requests.get(url)
    return r.text