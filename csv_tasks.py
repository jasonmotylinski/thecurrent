
import csv
import luigi
import os

from calendar import monthrange
from datetime import datetime
from html_tasks import SaveDayHtmlToLocal
from luigi.format import UTF8
from playlist import get_songs

CSV_HEADER_ROW = ['id', 'artist', 'title', 'album', 'played_at', 'duration', 'service_id', 'song_id', 'play_id', 
                  'composer', 'conductor', 'orch_ensemble', 'soloist_1', 'soloist_2', 'soloist_3', 'soloist_4',
                  'soloist_5', 'soloist_6', 'record_co', 'record_id', 'addl_text', 'broadcast', 'songs_on_album',
                  'songs_by_artist', 'album_mbid', 'art_url', 'year', 'month', 'day', 'day_of_week', 'week','hour']


class ConvertDayHtmlToCsv(luigi.Task):
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
            with open(self.output().path, 'w') as f:
                writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
                writer.writerow(CSV_HEADER_ROW)
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


class CreateYearCsv(luigi.WrapperTask):
    """Parse the articles from the HTML for the given year."""
    year = luigi.IntParameter()

    def requires(self):
        for i in range(1, 13):
            yield CreateMonthCsv(self.year, i)

class CreateYearRangeCsv(luigi.WrapperTask):
    """Parse the articles from the HTML for the given year."""
    beginyear = luigi.IntParameter()
    endyear = luigi.IntParameter()

    def requires(self):
        for year in range(self.beginyear, self.endyear + 1):
            for i in range(1, 13):
                yield CreateMonthCsv(year, i)
