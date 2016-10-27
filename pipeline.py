"""Pipeline for ingesting the current playlist."""
import luigi
from calendar import monthrange
from datetime import datetime
from models import Article
from playlist import get_hour, get_day

from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=['localhost'], timeout=60)
Article.init()


class GetHourTask(luigi.Task):
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


class GetDayTask(luigi.Task):
    """Get a days worth of playists."""
    date = luigi.DateParameter()

    def requires(self):
        for i in range(0, 24):
            yield GetHourTask(self.date, "{0:02d}".format(i))


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
