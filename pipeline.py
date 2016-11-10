"""Pipeline for ingesting the current playlist."""
import luigi
from calendar import monthrange
from datetime import datetime
from luigi.format import UTF8
from models import Article
from playlist import get_hour, get_day, get_day_html, get_articles

from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=['localhost'], timeout=60)
Article.init()

 
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
            with self.output().open('w') as f:
                results = get_articles(i.read(), self.date.year, self.date.month, self.date.day)
                list(f.write(",".join([r.id,
                                       r.datetime.isoformat(),
                                       r.artist,
                                       r.title,
                                       r.datetime.strftime("%Y"), 
                                       r.datetime.strftime("%m"), 
                                       r.datetime.strftime("%d"),
                                       r.datetime.strftime("%A"),
                                       r.datetime.strftime("%U"),
                                       r.datetime.strftime("%H")]) + "\n") for r in results)

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


class SaveHourToElasticsearch(luigi.Task):
    """Save articles for a given hour to Elasticsearch."""
    date = luigi.DateParameter()
    hour = luigi.Parameter()
    _is_completed = False

    def run(self):
        """Run."""
        results = get_hour(self.date.year, self.date.month, self.date.day, self.hour)
        for r in results:
            article = Article(meta={'_id': r.id}, artist=r.artist, title=r.title, datetime=r.datetime)
            article.save()
        self._is_completed = True

    def complete(self):
        return self._is_completed


class CsvDayToElasticsearch(luigi.Task):
    """Save a days worth of playists to Elasticsearch."""
    date = luigi.DateParameter()
    _is_completed = False

    def run(self):
        with self.input()[0].open('r') as i:
            for line in i:
                parts = line.split(',')
                article = Article(meta={'_id': parts[0]}, artist=parts[2], title=parts[3], datetime=parts[1])
                article.save()
        self._is_completed = True

    def requires(self):
        yield DayHtmlToArticlesCsv(self.date)

    def complete(self):
        return self._is_completed


class CsvMonthToElasticsearch(luigi.Task):
    """Save a months worth of playists to Elasticsearch."""
    year = luigi.Parameter()
    month = luigi.Parameter()

    def requires(self):
        month_days = monthrange(int(self.year), int(self.month))
        for i in range(1, month_days[1] + 1):
            yield CsvDayToElasticsearch(datetime(int(self.year), int(self.month), i))


class SaveDayToElasticsearch(luigi.Task):
    """Save a days worth of playists to Elasticsearch."""
    date = luigi.DateParameter()
    _is_completed = False

    def run(self):
        try:
            results = get_day(self.date.year, self.date.month, self.date.day)
            for r in results:
                article = Article(meta={'_id': r.id}, artist=r.artist, title=r.title, datetime=r.datetime)
                article.save()
            self._is_completed = True
        except:
            pass

    def complete(self):
        return self._is_completed


class SaveMonthToElasticsearch(luigi.Task):
    """Save a days worth of playists to Elasticsearch."""
    year = luigi.Parameter()
    month = luigi.Parameter()
    _is_completed = False

    def requires(self):
        month_days = monthrange(int(self.year), int(self.month))
        for i in range(1, month_days[1] + 1):
            yield SaveDayToElasticsearch(datetime(int(self.year), int(self.month), i))
        self._is_completed = True

    def complete(self):
        return self._is_completed


class SaveYearToElasticsearch(luigi.Task):
    """Save a days worth of playists to Elasticsearch."""
    year = luigi.Parameter()
    _is_completed = False

    def requires(self):
        for i in range(1, 13):
            yield SaveMonthToElasticsearch(self.year, i)
        self._is_completed = True

    def complete(self):
        return self._is_completed
