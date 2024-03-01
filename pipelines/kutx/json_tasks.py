import config
import luigi
import requests

from calendar import monthrange
from datetime import datetime
from pipelines import BaseSaveDayJsonToLocal


class SaveDayJsonToLocal(BaseSaveDayJsonToLocal):
    def __init__(self, *args, **kwargs):
        super(SaveDayJsonToLocal, self).__init__(*args, **kwargs)
        self.config= config.KUTX

    def get_json(self):
        r=requests.get(self.config.DAY_URL.format(date=self.date))
        return r.json()


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