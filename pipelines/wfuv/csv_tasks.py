import bs4 as bs
import config
import csv
import datetime
import json
import luigi
import os

from luigi.format import UTF8
from pipelines import create_id
from pipelines.wfuv.json_tasks import SaveDayJsonToLocal


class ConvertDayJsonToCsv(luigi.Task):
    """Parse the articles from the JSON for the given day."""
    date = luigi.DateParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget(config.WFUV.DAY_CSV.format(self.date.strftime("%Y"), self.date.strftime("%m"), self.date.strftime("%Y%m%d")),format=UTF8)

    def run(self):
        """Run."""
        with self.input()[0].open('r') as i:         
            d = os.path.dirname(self.output().path)
            if not os.path.exists(d):
                os.makedirs(d)
            with open(self.output().path, 'w') as f:
                writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
                writer.writerow(config.CSV_HEADER_ROW)
                tbody=bs.BeautifulSoup(json.load(i)[4]['data']).select_one('tbody')
                for tr in tbody.select('tr'):
                    dte=tr.find('td', {'headers': 'view-created-table-column'}).text.strip()
                    song=tr.find('td', {'headers': 'view-title-table-column'}).text.strip()
                    artist=tr.find('td', {'headers': 'view-field-artist-table-column'}).text.strip()
                    d=datetime.datetime.strptime(dte, "%m/%d, %H:%M%p")
                    played_at=d.replace(year=2023, tzinfo = datetime.timezone(offset=datetime.timedelta(hours=-5)))
        
                    writer.writerow([  create_id(played_at, artist, song, config.WFUV.SERVICE_ID), 
                                       artist,
                                        song,
                                        '',
                                        played_at.isoformat(),
                                        '', # Duration
                                        config.WFUV.SERVICE_ID, # Service ID
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
                                        played_at.strftime("%H")])

    def requires(self):
        """Requires."""
        yield SaveDayJsonToLocal(self.date)