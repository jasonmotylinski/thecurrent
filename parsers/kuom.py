import bs4 as bs
import json
from datetime import datetime, timezone, timedelta
from parsers import BaseParser


class KuomParser(BaseParser):

    def get_songs(self, reader):
        for day in json.load(reader):
            for spin in bs.BeautifulSoup(day['data']).select('li', {'class': 'spinitron_playlist__spin'}):
                song=spin.find('div',{'class': 'spinitron_playlist__spin--song'}).text.strip()
                artist=spin.find('div',{'class': 'spinitron_playlist__spin--artist'}).text.strip()
                tme=spin.find('div',{'class': 'spinitron_playlist__spin--start'}).text.strip()
                d=datetime.strptime(self._date.strftime("%Y-%m-%d") + " " + tme, "%Y-%m-%d %H:%M %p")
                played_at=d.replace(tzinfo=timezone(timedelta(hours=-5)))
                yield {"song": song, "artist": artist, "played_at": played_at}