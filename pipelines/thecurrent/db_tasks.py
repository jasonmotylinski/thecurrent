import config
import csv
import luigi
import sqlite3

from datetime import datetime, timedelta
from pipelines.thecurrent.csv_tasks import ConvertDayHtmlToCsv
from luigi.contrib import mysqldb
from pipelines import clean_str


class InsertDayDataMysql(mysqldb.CopyToTable):
    date = luigi.DateParameter()
    reflect = True
    database = config.DB_NAME
    host = config.DB_MYSQL_HOST
    password = config.DB_MYSQL_PASSWD
    user = config.DB_MYSQL_USER
    table = "songs" 
    columns = [['id'], ['artist'], ['title'], ['album'], ['played_at'], ['duration'], ['service_id'], ['song_id'], ['play_id'], 
               ['composer'], ['conductor'], ['orch_ensemble'], ['soloist_1'], ['soloist_2'], ['soloist_3'], ['soloist_4'], 
               ['soloist_5'], ['soloist_6'], ['record_co'], ['record_id'],['addl_text'], ['broadcast'], ['songs_on_album'],
               ['songs_by_artist'], ['album_mbid'], ['art_url'], ['year'], ['month'], ['day'], ['day_of_week'], ['week'], ['hour']]
    def rows(self):
        with self.input()[0].open('r') as f:
            reader=csv.DictReader(f, delimiter=',', quoting=csv.QUOTE_ALL)
            for row in reader:
                yield [clean_str(row['id']),clean_str(row['artist']),clean_str(row['title']),clean_str(row['album']),clean_str(row['played_at']),
                      clean_str(row['duration']),clean_str(row['service_id']), clean_str(row['song_id']),clean_str(row['play_id']),
                      clean_str(row['composer']), clean_str(row['conductor']), clean_str(row['orch_ensemble']),
                      clean_str(row['soloist_1']),clean_str(row['soloist_2']),clean_str(row['soloist_3']),clean_str(row['soloist_4']),
                      clean_str(row['soloist_5']),clean_str(row['soloist_6']),clean_str(row['record_co']),clean_str(row['record_id']),
                      clean_str(row['addl_text']),clean_str(row['broadcast']), clean_str(row['songs_on_album']),
                      clean_str(row['songs_by_artist']), clean_str(row['album_mbid']), clean_str(row['art_url']),
                      clean_str(row['year']), clean_str(row['month']), clean_str(row['day']),clean_str(row['day_of_week']), clean_str(row['week']),
                      clean_str(row['hour'])]
    def requires(self):
        """Requires."""
        yield ConvertDayHtmlToCsv(self.date)

class InsertDayData(luigi.Task):
    date = luigi.DateParameter()

    def run(self):
        with self.input()[0].open('r') as f:
            reader=csv.DictReader(f, delimiter=',', quoting=csv.QUOTE_ALL)
            for row in reader:
                t = """SELECT id
                    FROM songs
                    WHERE id='{id}'
                    LIMIT 1""".format(id=row['id'])
                con = sqlite3.connect(config.DB)
                results=con.execute(t).fetchall()
                if(len(results))==0:
                    t="""INSERT INTO songs VALUES({id}, {artist}, {title}, {album}, {played_at}, {duration}, {service_id},
                                                  {song_id}, {play_id}, {composer}, {conductor}, {orch_ensemble},
                                                  {soloist_1}, {soloist_2}, {soloist_3}, {soloist_4},{soloist_5},
                                                  {soloist_6}, {record_co}, {record_id}, {addl_text}, {broadcast}, 
                                                  {songs_on_album},{songs_by_artist}, {album_mbid}, {art_url}, 
                                                  {year}, {month}, {day}, {day_of_week}, {week},{hour})"""\
                                                    .format(id=clean_str(row['id']),artist=clean_str(row['artist']),title=clean_str(row['title']),album=clean_str(row['album']),played_at=clean_str(row['played_at']),
                                                            duration=clean_str(row['duration']),service_id=clean_str(row['service_id']), song_id=clean_str(row['song_id']),play_id=clean_str(row['play_id']),
                                                            composer=clean_str(row['composer']), conductor=clean_str(row['conductor']), orch_ensemble=clean_str(row['orch_ensemble']),
                                                            soloist_1=clean_str(row['soloist_1']),soloist_2=clean_str(row['soloist_2']),soloist_3=clean_str(row['soloist_3']),soloist_4=clean_str(row['soloist_4']),
                                                            soloist_5=clean_str(row['soloist_5']),soloist_6=clean_str(row['soloist_6']),record_co=clean_str(row['record_co']),record_id=clean_str(row['record_id']),
                                                            addl_text=clean_str(row['addl_text']),broadcast=clean_str(row['broadcast']), songs_on_album=clean_str(row['songs_on_album']),
                                                            songs_by_artist=clean_str(row['songs_by_artist']), album_mbid=clean_str(row['album_mbid']), art_url=clean_str(row['art_url']),
                                                            year=clean_str(row['year']), month=clean_str(row['month']), day=clean_str(row['day']), day_of_week=clean_str(row['day_of_week']), week=clean_str(row['week']),
                                                            hour=clean_str(row['hour']))
                    print(t)
                    con.execute(t)
                    con.commit()
                    

    def requires(self):
        """Requires."""
        yield ConvertDayHtmlToCsv(self.date)
        
class InsertDayRangeData(luigi.Task):
    end_date=luigi.DateParameter()
    start_date=luigi.DateParameter()

    def requires(self):
        for d in [self.start_date+timedelta(days=x) for x in range((self.end_date-self.start_date).days + 1)]:
            yield InsertDayData(d)

class KCMPBackfillLastXDaysData(luigi.Task):

    last_x_days=luigi.IntParameter()

    def run(self):

        con = sqlite3.connect(config.DB)
        sql = "DROP TABLE IF EXISTS songs_totals_by_day;"
        con.execute(sql)
        con.commit()

        sql = """CREATE TABLE songs_totals_by_day AS
                SELECT 
                    artist, 
                    title,
                    year || "-" || PRINTF('%02d', month) || "-" || PRINTF('%02d', day)  AS played_at_ymd,
                    COUNT(*) as ct
                FROM songs
                WHERE
                    artist != ''
                    AND title != ''
                GROUP BY
                    artist,
                    title,
                    year,
                    month,
                    day;"""
        con.execute(sql)
        con.commit()


    def requires(self):
        for d in [datetime.now()-timedelta(days=x) for x in range(1, self.last_x_days + 1)]:
            yield InsertDayData(d)