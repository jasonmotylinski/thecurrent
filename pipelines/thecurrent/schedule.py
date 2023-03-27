import config
import json
import requests

from bs4 import BeautifulSoup
from hashlib import sha256

def create_id(show): 
    key = "{0}{1}{2}".format(show["show_id"], show["host_name"], show["show_name"],show["start_time"], show["end_time"])
    m = sha256()
    m.update(key.encode("UTF-8"))
    return m.hexdigest()

def get_schedule_html(date):
    r=requests.get(config.THECURRENT_SCHEDULE_DAY_URL.format(date=date))
    return r.text

def get_shows(html):
    soup=BeautifulSoup(html, "html.parser")
    data=json.loads(soup.find("script", {"id":"__NEXT_DATA__"}).string)
    print(data['props']['pageProps']['data'].keys())
    for h in data['props']['pageProps']['data']['hosts']:
        show={
            'show_id': h['id'],
            'host_name': h['hostName'], 
            'show_name': h['showName'], 
            'start_time': h['startTime'],
            'end_time': h['endTime']
        }
        show['id']=create_id(show)
        yield(show)