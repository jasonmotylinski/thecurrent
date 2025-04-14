import bs4 as bs
import json
from datetime import datetime, timezone, timedelta
from parsers import BaseParser


class WfuvParser(BaseParser):

    def get_songs(self, reader):
        tbody=bs.BeautifulSoup(json.load(reader)[3]['data']).select_one('tbody')

        for tr in tbody.select('tr'):
            dte=tr.find('td', {'headers': 'view-created-table-column'}).text.strip()
            song=tr.find('td', {'headers': 'view-title-table-column'}).text.strip()
            artist=tr.find('td', {'headers': 'view-field-artist-table-column'}).text.strip()
            d=datetime.strptime(dte, "%m/%d, %I:%M%p")
            played_at=d.replace(year=int(self._date.strftime("%Y")), tzinfo = timezone(offset=timedelta(hours=-5)))
            yield {"song": song, "artist": artist, "played_at": played_at}
