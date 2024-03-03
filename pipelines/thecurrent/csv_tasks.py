
import config
import csv
import luigi
import os

from calendar import monthrange
from datetime import datetime
from pipelines.thecurrent.html_tasks import SaveDayHtmlToLocal, SaveScheduleDayHtmlToLocal
from luigi.format import UTF8
from pipelines.thecurrent.playlist import get_songs
from pipelines.thecurrent.schedule import get_shows

class ConvertDayHtmlToCsv(luigi.Task):
    """Parse the articles from the HTML for the given day."""
    date = luigi.DateParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget(config.THECURRENT_DAY_CSV.format(self.date.strftime("%Y"), self.date.strftime("%m"), self.date.strftime("%Y%m%d")),format=UTF8)

    def run(self):
        """Run."""
        with self.input()[0].open('r') as i:
            d = os.path.dirname(self.output().path)
            if not os.path.exists(d):
                os.makedirs(d)
            with open(self.output().path, 'w') as f:
                writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
                writer.writerow(config.CSV_HEADER_ROW)
                songs = get_songs(i.read())

                list(writer.writerow([s["id"], 
                                      s["artist"],
                                      s["title"],
                                      s["album"],
                                      s["played_at"],
                                      '', # Duration
                                      config.THECURRENT.SERVICE_ID, # Service_id
                                      '',
                                      '',
                                      '',
                                      '',
                                      '',
                                      '',
                                      '',
                                      '',
                                      '',
                                      '',
                                      '',
                                      '',
                                      '',
                                      '',
                                      '',
                                      '',
                                      '',
                                      '',
                                      '',
                                      s["played_at_dt"].strftime("%Y"),
                                      s["played_at_dt"].strftime("%m"),
                                      s["played_at_dt"].strftime("%d"),
                                      s["played_at_dt"].strftime("%A"),
                                      s["played_at_dt"].strftime("%U"),
                                      s["played_at_dt"].strftime("%H")]) for s in songs)

    def requires(self):
        """Requires."""
        yield SaveDayHtmlToLocal(self.date)

class CreateMonthCsv(luigi.WrapperTask):
    """Parse the articles from the HTML for the given month."""
    year = luigi.IntParameter()
    month = luigi.IntParameter()

    def requires(self):
        month_days = monthrange(int(self.year), int(self.month))
        for i in range(1, month_days[1] + 1):
            yield ConvertDayHtmlToCsv(datetime(int(self.year), int(self.month), i))


class CreateMonthCsvByYear(luigi.WrapperTask):
    """Parse the articles from the HTML for the given year."""
    year = luigi.IntParameter()

    def requires(self):
        for i in range(1, 13):
            yield CreateMonthCsv(self.year, i)

class CreateMonthCsvByYearRange(luigi.WrapperTask):
    """Parse the articles from the HTML for the given year."""
    beginyear = luigi.IntParameter()
    endyear = luigi.IntParameter()

    def requires(self):
        for year in range(self.beginyear, self.endyear + 1):
            for i in range(1, 13):
                yield CreateMonthCsv(year, i)


class CreateYearCsv(luigi.Task):
    """Combine all files for a given year into a single CSV."""
    year = luigi.IntParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget(config.THECURRENT_YEAR_CSV.format(self.year), format=UTF8)

    def run(self):
        """Run."""
        with open(self.output().path, "w") as y:
            writer = csv.writer(y, delimiter=',', quoting=csv.QUOTE_ALL)
            writer.writerow(config.CSV_HEADER_ROW)
            for month in range(1, 13):
                month_days = monthrange(int(self.year), int(month))
                for day in range(1, month_days[1] + 1):         
                    date="{0}{1:02d}{2:02d}".format(self.year, month,day)
                    with open(config.THECURRENT_DAY_CSV.format(self.year, "{0:02d}".format(month), date), "r") as f:
                        reader = csv.reader(f, delimiter=',')
                        next(reader, None)
                        for row in reader:
                            writer.writerow(row)

    def requires(self):
        """requires."""
        return CreateMonthCsvByYear(self.year)
    
class CreateYearCsvByYearRange(luigi.WrapperTask):
    """Create multiple year CSV files within the given range."""
    beginyear = luigi.IntParameter()
    endyear = luigi.IntParameter()

    def requires(self):
        for year in range(self.beginyear, self.endyear + 1):
            yield CreateYearCsv(year)

class ConvertScheduleDayHtmlToCsv(luigi.Task):
    """Parse the scheduel from the HTML for the given day."""
    date = luigi.DateParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget(config.THECURRENT_SCHEDULE_DAY_CSV.format(self.date.strftime("%Y"), self.date.strftime("%m"), self.date.strftime("%Y%m%d")),format=UTF8)

    def run(self):
        """Run."""
        with self.input()[0].open('r') as i:
            d = os.path.dirname(self.output().path)
            if not os.path.exists(d):
                os.makedirs(d)
            with open(self.output().path, 'w') as f:
                writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
                writer.writerow(config.THECURRENT_SCHEDULE_CSV_HEADER_ROW)
                shows = get_shows(i.read())

                list(writer.writerow([s["id"],
                                      s["show_id"], 
                                      s["host_name"],
                                      s["show_name"],
                                      s["start_time"],
                                      s["end_time"]
                                      ]) for s in shows)

    def requires(self):
        """Requires."""
        yield SaveScheduleDayHtmlToLocal(self.date)

class CreateScheduleMonthCsv(luigi.WrapperTask):
    """Parse the scheudle from the HTML for the given month."""
    year = luigi.IntParameter()
    month = luigi.IntParameter()

    def requires(self):
        month_days = monthrange(int(self.year), int(self.month))
        for i in range(1, month_days[1] + 1):
            yield ConvertScheduleDayHtmlToCsv(datetime(int(self.year), int(self.month), i))

class CreateScheduleYearCsv(luigi.Task):
    """Combine all files for a given year into a single CSV."""
    year = luigi.IntParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget(config.THECURRENT_SCHDEULE_YEAR_CSV.format(self.year), format=UTF8)

    def run(self):
        """Run."""
        with open(self.output().path, "w") as y:
            writer = csv.writer(y, delimiter=',', quoting=csv.QUOTE_ALL)
            writer.writerow(config.THECURRENT_SCHEDULE_CSV_HEADER_ROW)
            for month in range(1, 13):
                month_days = monthrange(int(self.year), int(month))
                for day in range(1, month_days[1] + 1):
                    with open(config.THECURRENT_SCHEDULE_DAY_CSV.format(self.year, "{0:02d}".format(month),  "{0}{1:02d}{2:02d}".format(self.year, month, day)), "r") as f:
                        reader = csv.reader(f, delimiter=',')
                        next(reader, None)
                        for row in reader:
                            writer.writerow(row)
    
    def requires(self):
        for month in range(1, 13):
            month_days = monthrange(int(self.year), month)
            for i in range(1, month_days[1] + 1):
                yield ConvertScheduleDayHtmlToCsv(datetime(int(self.year), month, i))
