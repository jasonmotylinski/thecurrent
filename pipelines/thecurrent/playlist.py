import config
import json
import requests

from bs4 import BeautifulSoup
from dateutil import parser
from hashlib import sha256



def create_id(song): 
    key = "{0}{1}{2}".format(song["played_at"], song["artist"], song["title"])
    m = sha256()
    m.update(key.encode("UTF-8"))
    return m.hexdigest()

def get_songs(html):
    """Get the articles for a given year, month, day, hour."""
    bs=BeautifulSoup(html, "html.parser")
    data=json.loads(bs.find("script", {"id":"__NEXT_DATA__"}).string)
    for s in data["props"]["pageProps"]["data"]["songs"]:
        s["id"] = create_id(s)
        s["played_at_dt"] = parser.parse(s["played_at"])
        yield(s)

def get_hour_html(year:int, month:int, day:int, hour:int):
    url=config.THECURRENT_HOUR_URL.format(year=year, month=month, day=day, hour=hour)
    r=requests.get(url)
    return r.text


def get_day_html(year:int, month:int, day:int):
    url=config.THECURRENT_DAY_URL.format(year=year, month=month, day=day)
    r=requests.get(url)
    return r.text