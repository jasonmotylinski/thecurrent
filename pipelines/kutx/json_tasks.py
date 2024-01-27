import config
import json
import luigi
import requests

from calendar import monthrange
from datetime import datetime


class SaveDayJsonToLocal(luigi.Task):
    """Get an hour of playlist."""
    date = luigi.DateParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget(config.KUTX_DAY_JSON.format(year=int(self.date.strftime("%Y")), month=int(self.date.strftime("%m")), day=int(self.date.strftime("%d"))))

    def run(self):
        """Run."""
        with self.output().open('w') as f:
            r=requests.get(config.KUTX_DAY_URL.format(date=self.date))

            f.write(json.dumps(r.json(), indent=4))

class SaveMonthJsonToLocal(luigi.Task):
    """Save the HTML for a given month locally."""
    year = luigi.IntParameter()
    month = luigi.IntParameter()

    def requires(self):
        month_days = monthrange(int(self.year), int(self.month))
        for i in range(1, month_days[1] + 1):
            yield SaveDayJsonToLocal(datetime(int(self.year), int(self.month), i))

class SaveYearJsonToLocal(luigi.Task):
    """Save the HTML for a given month locally."""
    year = luigi.IntParameter()

    def requires(self):
        for i in range(1, 13):
            yield SaveMonthJsonToLocal(self.year, i)