"""Pipeline for ingesting the current playlist."""
import csv
import luigi
import os

from calendar import monthrange
from chartshow import get_chartshow_html, get_chartshow, get_chartshow_csv
from datetime import datetime, date, timedelta
from luigi.format import UTF8
from playlist import get_hour, get_day_html, get_articles


class SaveHourToLocal(luigi.Task):
    """Get an hour of playlist."""
    date = luigi.DateParameter()
    hour = luigi.Parameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget('thecurrent_{0}{1}.txt'.format(self.date.strftime("%Y%m%d"), self.hour))

    def run(self):
        """Run."""
        results = get_hour(self.date.year, self.date.month, self.date.day, self.hour)
        with self.output().open('w') as f:
            list(f.write(",".join([r.id, r.datetime.isoformat(), r.artist, r.title]) + "\n") for r in results)


class SaveDayToLocal(luigi.Task):
    """Get a days worth of playists."""
    date = luigi.DateParameter()

    def requires(self):
        for i in range(0, 24):
            yield SaveHourToLocal(self.date, "{0:02d}".format(i))


class SaveDayHtmlToLocal(luigi.Task):
    """Save the HTML for a given day locally."""
    date = luigi.DateParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget('output/html/{0}/{1}/playlist_{2}.html'.format(self.date.strftime("%Y"), self.date.strftime("%m"), self.date.strftime("%Y%m%d")))

    def run(self):
        with self.output().open('w') as f:
            f.write(get_day_html(self.date.year, self.date.month, self.date.day))


class DayHtmlToArticlesCsv(luigi.Task):
    """Parse the articles from the HTML for the given day."""
    date = luigi.DateParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget('output/csv/{0}/{1}/{2}.csv'.format(self.date.strftime("%Y"), self.date.strftime("%m"), self.date.strftime("%Y%m%d")),format=UTF8)

    def run(self):
        """Run."""
        with self.input()[0].open('r') as i:
            d = os.path.dirname(self.output().path)
            if not os.path.exists(d):
                os.makedirs(d)
            with open(self.output().path, 'wb') as f:
                results = get_articles(i.read(), self.date.year, self.date.month, self.date.day)
                writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
                writer.writerow(['id', 'datetime', 'artist', 'title', 'year', 'month', 'day', 'day_of_week', 'week', 'hour'])
                list(writer.writerow([r.id,
                                      r.datetime.isoformat(),
                                      r.artist.encode("utf-8"),
                                      r.title.encode("utf-8"),
                                      r.datetime.strftime("%Y"),
                                      r.datetime.strftime("%m"),
                                      r.datetime.strftime("%d"),
                                      r.datetime.strftime("%A"),
                                      r.datetime.strftime("%U"),
                                      r.datetime.strftime("%H")]) for r in results)

    def requires(self):
        """Requires."""
        yield SaveDayHtmlToLocal(self.date)


class SaveMonthHtmlToLocal(luigi.Task):
    """Save the HTML for a given month locally."""
    year = luigi.Parameter()
    month = luigi.Parameter()

    def requires(self):
        month_days = monthrange(int(self.year), int(self.month))
        for i in range(1, month_days[1] + 1):
            yield SaveDayHtmlToLocal(datetime(int(self.year), int(self.month), i))


class MonthHtmlToArticlesCsv(luigi.WrapperTask):
    """Parse the articles from the HTML for the given month."""
    year = luigi.Parameter()
    month = luigi.Parameter()

    def requires(self):
        max_days = monthrange(int(self.year), int(self.month))[0]
        if self.year == datetime.now().year \
           and self.month == datetime.now().month \
           and max_days > datetime.now().day:
            max_days = datetime.now().day
        for i in range(1, max_days):
            yield DayHtmlToArticlesCsv(datetime(int(self.year), int(self.month), i))


class YearHtmlToArticlesCsv(luigi.WrapperTask):
    """Parse the articles from the HTML for the given year."""
    year = luigi.Parameter()

    def requires(self):
        max_month = 13
        if int(self.year) == datetime.now().year:
            max_month = datetime.now().month
        for i in range(1, max_month):
            yield MonthHtmlToArticlesCsv(self.year, i)


class CombineYearArticlesCsv(luigi.Task):
    """Combine all files for a given year into a single CSV."""
    year = luigi.Parameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget('output/csv/{0}.csv'.format(self.year), format=UTF8)

    def run(self):
        """Run."""
        with open(self.output().path, "w") as y:
            writer = csv.writer(y, delimiter=',', quoting=csv.QUOTE_ALL)
            writer.writerow(['id', 'datetime', 'artist', 'title', 'year', 'month', 'day', 'day_of_week', 'week', 'hour'])

            max_month = 13
            if self.year == datetime.now().year:
                max_month = datetime.now().month + 1
            for month in range(1, max_month):
                max_days = monthrange(int(self.year), int(month))[0] + 1
                if max_days > datetime.now().day:
                    max_days = datetime.now().day
                for day in range(1, max_days):
                    with open('output/csv/{0}/{1}/{0}{1}{2}.csv'.format(self.year, "{0:02d}".format(month), "{0:02d}".format(day)), "r") as f:
                        reader = csv.reader(f, delimiter=',')
                        next(reader, None)
                        for row in reader:
                            writer.writerow(row)

    def requires(self):
        """requires."""
        return YearHtmlToArticlesCsv(str(self.year))


class SaveChartshowHtmlToLocal(luigi.Task):
    """Save the HTML for a given day locally."""
    date = luigi.DateParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget('output/html/chartshow/{0}/chartshow_{2}.html'.format(self.date.strftime("%Y"), self.date.strftime("%m"), self.date.strftime("%Y%m%d")))

    def run(self):
        with self.output().open('w') as f:
            try:
                f.write(get_chartshow_html(self.date.year, self.date.month, self.date.day))
            except:
                pass


class SaveAllChartshowHtmlForYearToLocal(luigi.Task):
    """Save the HTML for all Chart Show's for a given year."""
    year = luigi.IntParameter()

    def last_wednesday(self):
        today = date(self.year, 12, 31)
        if today >= date.today():
            today = date.today()
        offset = (today.weekday() - 2) % 7
        return today - timedelta(days=offset)

    def requires(self):
        """requires."""
        d = self.last_wednesday()
        while d.year == self.year and d <= date.today():
            yield SaveChartshowHtmlToLocal(d)
            d -= timedelta(days=7)


class ChartshowHtmlToChartshowRaw(luigi.Task):
    """Parse the chartshow from the HTML for the given day."""
    date = luigi.DateParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget('output/raw/chartshow/{0}/{1}.csv'.format(self.date.strftime("%Y"), self.date.strftime("%Y%m%d")), format=UTF8)

    def run(self):
        """Run."""
        with self.input()[0].open('r') as i:
            d = os.path.dirname(self.output().path)
            if not os.path.exists(d):
                os.makedirs(d)
            with open(self.output().path, 'wb') as f:
                results = get_chartshow(i.read(), self.date.year, self.date.month, self.date.day)
                f.write(results)

    def requires(self):
        """Requires."""
        yield SaveChartshowHtmlToLocal(self.date)


class SaveAllChartshowForYearRaw(luigi.Task):
    """Extract all raw data for all Chart Show's for a given year."""
    year = luigi.IntParameter()

    def last_wednesday(self):
        today = date(self.year, 12, 31)
        if today >= date.today():
            today = date.today()
        offset = (today.weekday() - 2) % 7
        return today - timedelta(days=offset)

    def requires(self):
        """requires."""
        d = self.last_wednesday()
        while d.year == self.year and d <= date.today():
            yield ChartshowHtmlToChartshowRaw(d)
            d -= timedelta(days=7)


class ChartshowRawToCsv(luigi.Task):
    """Convert the raw chartshow data to CSV."""
    date = luigi.DateParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget('output/csv/chartshow/{0}/{1}.csv'.format(self.date.strftime("%Y"), self.date.strftime("%Y%m%d")), format=UTF8)

    def run(self):
        """Run."""
        with self.input()[0].open('r') as i:
            d = os.path.dirname(self.output().path)
            if not os.path.exists(d):
                os.makedirs(d)
            with open(self.output().path, 'wb') as f:
                writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
                results = get_chartshow_csv(i.read())
                writer.writerow(['rank', 'date', 'artist', 'title'])
                list(writer.writerow([r["rank"],
                                      self.date.isoformat(),
                                      r["artist"].encode("utf-8"),
                                      r["title"].encode("utf-8")]) for r in results)

    def requires(self):
        """requires."""
        yield ChartshowHtmlToChartshowRaw(self.date)


class SaveAllChartshowRawForYearToCsv(luigi.Task):
    """Convert the raw chartshow data to CSV for a given year."""
    year = luigi.IntParameter()

    def last_wednesday(self):
        today = date(self.year, 12, 31)
        if today >= date.today():
            today = date.today()
        offset = (today.weekday() - 2) % 7
        return today - timedelta(days=offset)

    def requires(self):
        """requires."""
        d = self.last_wednesday()
        while d.year == self.year and d <= date.today():
            yield ChartshowRawToCsv(d)
            d -= timedelta(days=7)
