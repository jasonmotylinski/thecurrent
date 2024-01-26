import config
import csv
import json
import luigi
import os

from calendar import monthrange
from datetime import datetime
from luigi.format import UTF8
from pipelines import create_id
from pipelines.kexp.json_tasks import SaveDayJsonToLocal


class ConvertDayJsonToCsv(luigi.Task):
    """Parse the articles from the JSON for the given day."""
    date = luigi.DateParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget(config.KEXP_DAY_CSV.format(self.date.strftime("%Y"), self.date.strftime("%m"), self.date.strftime("%Y%m%d")),format=UTF8)

    def run(self):
        """Run."""
        with self.input()[0].open('r') as i:
            records=json.load(i)["results"]
            d = os.path.dirname(self.output().path)
            if not os.path.exists(d):
                os.makedirs(d)
            with open(self.output().path, 'w') as f:

                writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
                writer.writerow(config.CSV_HEADER_ROW)

                list(writer.writerow([  create_id(s["airdate"], s["artist"], s["song"], 2), 
                                        s["artist"],
                                        s["song"],
                                        s["album"],
                                        s["airdate"],
                                        '', # Duration
                                        '2', # Service ID
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
                                        datetime.fromisoformat(s["airdate"]).strftime("%Y"),
                                        datetime.fromisoformat(s["airdate"]).strftime("%m"),
                                        datetime.fromisoformat(s["airdate"]).strftime("%d"),
                                        datetime.fromisoformat(s["airdate"]).strftime("%A"),
                                        datetime.fromisoformat(s["airdate"]).strftime("%U"),
                                        datetime.fromisoformat(s["airdate"]).strftime("%H")]) for s in records if s["play_type"]=="trackplay")

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

