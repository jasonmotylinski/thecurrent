"""Pipeline for ingesting the current playlist."""
import csv
import luigi
import os
from calendar import monthrange
from datetime import datetime
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


class MonthHtmlToArticlesCsv(luigi.Task):
    """Parse the articles from the HTML for the given month."""
    year = luigi.Parameter()
    month = luigi.Parameter()

    def requires(self):
        month_days = monthrange(int(self.year), int(self.month))
        for i in range(1, month_days[1] + 1):
            yield DayHtmlToArticlesCsv(datetime(int(self.year), int(self.month), i))


class YearHtmlToArticlesCsv(luigi.Task):
    """Parse the articles from the HTML for the given year."""
    year = luigi.Parameter()

    def requires(self):
        for i in range(1, 13):
            yield MonthHtmlToArticlesCsv(self.year, i)


class CombineYearArticlesCsv(luigi.Task):
    """Combine all files for a given year into a single CSV."""
    year = luigi.Parameter()
