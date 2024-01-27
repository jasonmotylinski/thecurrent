import config
import csv
import json
import luigi
import os

from calendar import monthrange
from datetime import datetime
from pipelines import create_id
from luigi.format import UTF8
from pipelines.wxpn.json_tasks import SaveDayJsonToLocal


class ConvertDayJsonToCsv(luigi.Task):
    """Parse the articles from the JSON for the given day."""
    date = luigi.DateParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget(config.WXPN.DAY_CSV.format(self.date.strftime("%Y"), self.date.strftime("%m"), self.date.strftime("%Y%m%d")),format=UTF8)

    def run(self):
        """Run."""
        with self.input()[0].open('r') as i:         
            d = os.path.dirname(self.output().path)
            if not os.path.exists(d):
                os.makedirs(d)
            with open(self.output().path, 'w') as f:
                writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
                writer.writerow(config.CSV_HEADER_ROW)
                for s in json.load(i):
                    played_at=datetime.strptime(s["timeslice"]+"-05:00", "%Y-%m-%d %H:%M:%S%z") 
                    writer.writerow([  create_id(played_at, s["artist"], s["song"], config.KUTX.SERVICE_ID), 
                                        s["artist"],
                                        s["song"],
                                         s["album"],
                                        played_at.isoformat(),
                                        '', # Duration
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

