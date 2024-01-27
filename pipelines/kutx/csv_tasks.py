import config
import csv
import json
import luigi
import os

from calendar import monthrange
from datetime import datetime
from luigi.format import UTF8
from pipelines import create_id
from pipelines.kutx.json_tasks import SaveDayJsonToLocal


class ConvertDayJsonToCsv(luigi.Task):
    """Parse the articles from the JSON for the given day."""
    date = luigi.DateParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget(config.KUTX.DAY_CSV.format(self.date.strftime("%Y"), self.date.strftime("%m"), self.date.strftime("%Y%m%d")),format=UTF8)

    def run(self):
        """Run."""
        with self.input()[0].open('r') as i:         
            d = os.path.dirname(self.output().path)
            if not os.path.exists(d):
                os.makedirs(d)
            with open(self.output().path, 'w') as f:
                writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
                writer.writerow(config.CSV_HEADER_ROW)
                for p in json.load(i)["onToday"]:
                        records=p['playlist']
                        if records:
                            for s in records:
                                played_at=datetime.strptime(s["_start_time"]+"-06:00", "%m-%d-%Y %H:%M:%S%z") 
                                album=None
                                if 'collectionName' in s:
                                    album=s["collectionName"]
                                writer.writerow([  create_id(played_at, s["artistName"], s["trackName"], config.KUTX.SERVICE_ID), 
                                                    s["artistName"],
                                                    s["trackName"],
                                                    album,
                                                    played_at.isoformat(),
                                                    s["_duration"], # Duration
                                                    config.KUTX.SERVICE_ID, # Service ID
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


class CreateMonthCsv(luigi.WrapperTask):
    """Parse the articles from the HTML for the given month."""
    year = luigi.IntParameter()
    month = luigi.IntParameter()

    def requires(self):
        month_days = monthrange(int(self.year), int(self.month))
        for i in range(1, month_days[1] + 1):
            yield ConvertDayJsonToCsv(datetime(int(self.year), int(self.month), i))

