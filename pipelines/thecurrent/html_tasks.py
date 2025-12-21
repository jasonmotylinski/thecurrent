import config
import luigi

from calendar import monthrange
from datetime import datetime
from luigi.format import UTF8
from pipelines.thecurrent.playlist import get_hour_html, get_day_html
from parsers.kcmp import get_schedule_html

class SaveHourHtmlToLocal(luigi.Task):
    """Get an hour of playlist."""
    date = luigi.DateParameter()
    hour = luigi.IntParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget(config.THECURRENT_HOUR_HTML.format(year=int(self.date.strftime("%Y")), month=int(self.date.strftime("%m")), day=int(self.date.strftime("%d")), hour=self.hour))

    def run(self):
        """Run."""
        with self.output().open('w') as f:
            f.write(get_hour_html(self.date.year, self.date.month, self.date.day, self.hour))

class Save24HoursofHtmlToLocal(luigi.Task):
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
        return luigi.LocalTarget(config.THECURRENT_DAY_HTML.format(year=int(self.date.strftime("%Y")), month=int(self.date.strftime("%m")), day=int(self.date.strftime("%d"))))

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

class SaveScheduleDayHtmlToLocal(luigi.Task):
    """Save HTML for a day schedule."""
    date = luigi.DateParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget(config.THECURRENT_SCHEDULE_DAY_HTML.format(year=int(self.date.strftime("%Y")), month=int(self.date.strftime("%m")), day=int(self.date.strftime("%d"))))

    def run(self):
        """Run."""
        with self.output().open('w') as f:
            f.write(get_schedule_html(self.date))

class SaveScheduleMonthHtmlToLocal(luigi.Task):
    """Save the HTML for a month of schedules."""
    year=luigi.IntParameter()
    month=luigi.IntParameter()

    def requires(self):
        month_days = monthrange(int(self.year), int(self.month))
        for i in range(1, month_days[1] + 1):
            yield SaveScheduleDayHtmlToLocal(datetime(int(self.year), int(self.month), i))

class SaveScheduleYearHtmlToLocal(luigi.Task):
    """Save the HTML for year of schedules."""
    year=luigi.IntParameter()

    def requires(self):
        for i in range(1, 13):
            yield SaveScheduleMonthHtmlToLocal(self.year, i)

class SaveScheduleYearRangeHtmlToLocal(luigi.Task):
    """Save the HTML for year of schedules."""
    start_year=luigi.IntParameter()
    end_year=luigi.IntParameter()
    def requires(self):
        for y in range(self.start_year, self.end_year+1):
            for i in range(1, 13):
                yield SaveScheduleMonthHtmlToLocal(y, i)