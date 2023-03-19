
import config
import luigi

from calendar import monthrange
from datetime import datetime
from luigi.format import UTF8
from pipelines.thecurrent.playlist import get_hour_html, get_day_html

class SaveHourHtmlToLocal(luigi.Task):
    """Get an hour of playlist."""
    date = luigi.DateParameter()
    hour = luigi.IntParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget(config.HOUR_HTML.format(year=int(self.date.strftime("%Y")), month=int(self.date.strftime("%m")), day=int(self.date.strftime("%d")), hour=self.hour))

    def run(self):
        """Run."""
        with self.output().open('w') as f:
            f.write(get_hour_html(self.date.year, self.date.month, self.date.day, self.hour))

class SaveDayHtmlToLocal(luigi.Task):
    """Get a days worth of playists."""
    date = luigi.DateParameter()

    def requires(self):
        for i in range(0, 24):
            yield SaveHourHtmlToLocal(self.date, i)

class SaveDayHtmlToLocal(luigi.Task):
    """Get an hour of playlist."""
    date = luigi.DateParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget(config.DAY_HTML.format(year=int(self.date.strftime("%Y")), month=int(self.date.strftime("%m")), day=int(self.date.strftime("%d"))))

    def run(self):
        """Run."""
        with self.output().open('w') as f:
            f.write(get_day_html(self.date.year, self.date.month, self.date.day))

class SaveMonthHtmlToLocal(luigi.Task):
    """Save the HTML for a given month locally."""
    year = luigi.IntParameter()
    month = luigi.IntParameter()

    def requires(self):
        month_days = monthrange(int(self.year), int(self.month))
        for i in range(1, month_days[1] + 1):
            yield SaveDayHtmlToLocal(datetime(int(self.year), int(self.month), i))

class SaveYearHtmlToLocal(luigi.Task):
    """Save the HTML for a given month locally."""
    year = luigi.IntParameter()

    def requires(self):
        for i in range(1, 13):
            yield SaveMonthHtmlToLocal(self.year, i)
