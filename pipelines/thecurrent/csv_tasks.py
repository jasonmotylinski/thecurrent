
import config
import csv
import luigi
import os

from calendar import monthrange
from datetime import datetime
from pipelines.thecurrent.html_tasks import SaveDayHtmlToLocal
from luigi.format import UTF8
from pipelines.thecurrent.playlist import get_songs


class ConvertDayHtmlToCsv(luigi.Task):
    """Parse the articles from the HTML for the given day."""
    date = luigi.DateParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget(config.DAY_CSV.format(self.date.strftime("%Y"), self.date.strftime("%m"), self.date.strftime("%Y%m%d")),format=UTF8)

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
                                      s["duration"],
                                      s["service_id"],
                                      s["song_id"],
                                      s["play_id"],
                                      s["composer"],
                                      s["conductor"],
                                      s["orch_ensemble"],
                                      s["soloist_1"],
                                      s["soloist_2"],
                                      s["soloist_3"],
                                      s["soloist_4"],
                                      s["soloist_5"],
                                      s["soloist_6"],
                                      s["record_co"],
                                      s["record_id"],
                                      s["addl_text"],
                                      s["broadcast"],
                                      s["songs_on_album"],
                                      s["songs_by_artist"],
                                      s["album_mbid"],
                                      s["art_url"],
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
        return luigi.LocalTarget(config.YEAR_CSV.format(self.year), format=UTF8)

    def run(self):
        """Run."""
        with open(self.output().path, "w") as y:
            writer = csv.writer(y, delimiter=',', quoting=csv.QUOTE_ALL)
            writer.writerow(config.CSV_HEADER_ROW)
            for month in range(1, 13):
                month_days = monthrange(int(self.year), int(month))
                for day in range(1, month_days[1] + 1):
                    with open(config.DAY_CSV.format(self.year, "{0:02d}".format(month), "{0:02d}".format(day)), "r") as f:
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