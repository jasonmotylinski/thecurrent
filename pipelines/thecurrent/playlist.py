import config
import json
import logging
import requests
import re

from datetime import datetime
from hashlib import sha256

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.thecurrent.org/",
    "Connection": "keep-alive",
}


def create_id(played_at, artist, title): 
    key = "{0}{1}{2}".format(played_at, artist, title)
    m = sha256()
    m.update(key.encode("UTF-8"))
    return m.hexdigest()

def get_songs(html):
    """Get the articles for a given year, month, day, hour."""
    pattern = r'\\"plays\\":(.*)},\\"d'
    match = re.search(pattern, html)
    if match:
        data = json.loads(match.group(1).replace('\\\\', '\\').replace('\\"', '"'))
        
        for d in data:
            item = {
                    "title": d['song']['title'],
                    "artist": d['song']['artist'],
                    "album":  d['song']['album'],
                    "played_at": datetime.fromisoformat(d['played_at'])
                }
            item["id"] = create_id(item['played_at'], item['artist'], item['title'])
            item["played_at_dt"] = item['played_at']
            yield(item)

def get_hour_html(year:int, month:int, day:int, hour:int):
    url=config.THECURRENT_HOUR_URL.format(year=year, month=month, day=day, hour=hour)
    logging.info("get_hour_html: url: {0}".format(url))
    r=requests.get(url, headers=headers, timeout=10)

    return r.text


def get_day_html(year:int, month:int, day:int):
    url=config.THECURRENT_DAY_URL.format(year=year, month=month, day=day)
    logging.info("get_day_html: url: {0}".format(url))
    r=requests.get(url, headers=headers, timeout=10)
    return r.text