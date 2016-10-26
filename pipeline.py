"""Pipeline for ingesting the current playlist."""
import luigi
from playlist import get_hour


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
