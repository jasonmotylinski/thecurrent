import bs4 as bs
import config
import json
import luigi
from datetime import datetime, timezone, timedelta
from pipelines import create_id, BaseConvertDayJsonToCsv
from pipelines.wfuv.json_tasks import SaveDayJsonToLocal


class ConvertDayJsonToCsv(BaseConvertDayJsonToCsv):
    """Parse the articles from the JSON for the given day."""
    date = luigi.DateParameter()

    def __init__(self, *args, **kwargs):
        super(ConvertDayJsonToCsv, self).__init__(*args, **kwargs)
        self.config= config.WFUV

    def requires(self):
        """Requires."""
        yield SaveDayJsonToLocal(self.date)
        
    def get_rows(self, input):
        tbody=bs.BeautifulSoup(json.load(input)[4]['data']).select_one('tbody')
        for tr in tbody.select('tr'):
            dte=tr.find('td', {'headers': 'view-created-table-column'}).text.strip()
            song=tr.find('td', {'headers': 'view-title-table-column'}).text.strip()
            artist=tr.find('td', {'headers': 'view-field-artist-table-column'}).text.strip()
            d=datetime.strptime(dte, "%m/%d, %H:%M%p")
            played_at=d.replace(year=int(self.date.strftime("%Y")), tzinfo = timezone(offset=timedelta(hours=-5)))

            yield [create_id(played_at, artist, song, self.config.SERVICE_ID), 
                    artist,
                    song,
                    '',
                    played_at.isoformat(),
                    '', # Duration
                    self.config.SERVICE_ID, # Service ID
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    played_at.strftime("%Y"),
                    played_at.strftime("%m"),
                    played_at.strftime("%d"),
                    played_at.strftime("%A"),
                    played_at.strftime("%U"),
                    played_at.strftime("%H")]

