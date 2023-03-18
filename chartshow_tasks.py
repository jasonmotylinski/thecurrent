
import csv
import luigi
import os

from chartshow import get_chartshow_html, get_chartshow, get_chartshow_csv
from datetime import date, timedelta
from luigi.format import UTF8

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
