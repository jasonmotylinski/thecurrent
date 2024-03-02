import config
import csv
import json
import luigi
import os
import sqlite3
from calendar import monthrange
from datetime import datetime, timedelta
from hashlib import sha256
from luigi.format import UTF8


def sub_import(x):
    groups = x.split('.') 
    module = ".".join(groups[:-1])
    b = __import__( module ) 
    for comp in groups[1:]: 
        b = getattr(b, comp) 
    return b 

def clean_str(str):
    newval= str.replace('"', '""')
    if newval == '':
       return "NULL"
    if newval == 'True':
        newval = 1
    if newval == 'False':
        newval = 0
    return "\"{0}\"".format(newval)

def create_id(played_at, artist, title, source): 
    key = "{0}{1}{2}{3}".format(played_at, artist, title, source)
    m = sha256()
    m.update(key.encode("UTF-8"))
    return m.hexdigest()

class BaseSaveDayJsonToLocal(luigi.Task):
    """Base class for retrieving JSON-based playlist information

    Args:
        luigi (Task): luigi.Task base class

    Raises:
        NotImplementedError: Thrown when the get_json() method is not overwritten by the inheriting class

    Returns:
        BaseSaveDayJsonToLocal: BaseSaveDayJsonToLocal
    """
    date = luigi.DateParameter()
    config = {}

    def output(self):
        """The local output target destination 

        Returns:
            LocalTarget: An object repreenting the output
        """
        return luigi.LocalTarget(self.config.DAY_JSON.format(year=int(self.date.strftime("%Y")), month=int(self.date.strftime("%m")), day=int(self.date.strftime("%d"))))

    def get_json(self):
        """Abstract class for retrieving a JSON-based playlist from the radio station source

        Raises:
            NotImplementedError: Thrown when the inheriting child class does not override this method
        """
        raise NotImplementedError
    
    def run(self):
        """Runs the task by calling get_json() and saving the results to the output()
        """
        with self.output().open('w') as f:
            f.write(json.dumps(self.get_json(), indent=4))

class SaveMonthJsonToLocal(luigi.Task):
    """Save the JSON for a given month locally."""
    year = luigi.IntParameter()
    month = luigi.IntParameter()
    service_name = luigi.Parameter()

    def requires(self):
        """Yields a month's worth of SaveDayJsonToLocal tasks for the given service, year, and month

        Yields:
            luigi.Task: The dynamically loaded SaveDayJsonToLocal task for given service
        """
        month_days = monthrange(int(self.year), int(self.month))
        for i in range(1, month_days[1] + 1):
            task = sub_import("pipelines.{0}.json_tasks.SaveDayJsonToLocal".format(self.service_name)) 
            yield task(datetime(int(self.year), int(self.month), i))

class SaveYearJsonToLocal(luigi.Task):
    """Save the JSON for a given year locally."""
    year = luigi.IntParameter()
    service_name = luigi.Parameter()

    def requires(self):
        """Yields tasks for the given year

        Yields:
            luigi.Task: Monthly tasks for the given year
        """
        for i in range(1, 13):
            yield SaveMonthJsonToLocal(self.year, i, self.service_name)

class BaseConvertDayJsonToCsv(luigi.Task):
    """Parse the songs from the JSON for the given day."""
    date = luigi.DateParameter()
    config = {}

    def output(self):
        """The local output target destination 

        Returns:
            LocalTarget: An object repreenting the output
        """
        return luigi.LocalTarget(self.config.DAY_CSV.format(self.date.strftime("%Y"), self.date.strftime("%m"), self.date.strftime("%Y%m%d")),format=UTF8)

    def get_rows(self, input):
        """Gets the CSV rows from the input to be written to the CSV file

        Args:
            input (FileHandler): The open file handler to the inputfit

        Raises:
            NotImplementedError: Raised when the child class hasn't correctly overridden this function
        """
        raise NotImplementedError

    def run(self):
        """Runs the task by calling get_rows() and saving the results to the output()
        """
        with self.input()[0].open('r') as i:         
            d = os.path.dirname(self.output().path)
            if not os.path.exists(d):
                os.makedirs(d)
            with open(self.output().path, 'w') as f:
                writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
                writer.writerow(config.CSV_HEADER_ROW)
                writer.writerows(self.get_rows(i))
                
class CreateMonthCsv(luigi.WrapperTask):
    """Parse the articles from the HTML for the given month."""
    year = luigi.IntParameter()
    month = luigi.IntParameter()
    service_name = luigi.Parameter()

    def requires(self):
        """Yields a list of CSV tasks for the given year, month, and service

        Yields:
            luigi.Task: The ConvertDayJsonToCsv tasks for the given year, month, and service
        """
        month_days = monthrange(int(self.year), int(self.month))
        for i in range(1, month_days[1] + 1):
            task = sub_import("pipelines.{0}.csv_tasks.ConvertDayJsonToCsv".format(self.service_name)) 
            yield task(datetime(int(self.year), int(self.month), i))

class InsertDayData(luigi.Task):
    """Inserts the given day's data into the database
    """
    date = luigi.DateParameter()
    service_name = luigi.Parameter()
    
    def requires(self):
        """Requires the ConvertDayJsonToCsv task to run

        Yields:
            luigi.Task: The ConvertDayJsonToCsv of the service 
        """
        task = sub_import("pipelines.{0}.csv_tasks.ConvertDayJsonToCsv".format(self.service_name)) 
        yield task(self.date)

    def run(self):
        """Reads the data output from the ConvertDayJsonToCsv task and inserts the data into the database.
        Checks for duplicates using the id column 
        """
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

class InsertDayRangeData(luigi.Task):
    """Inserts the start to end date range of data into the databse"""
    end_date=luigi.DateParameter()
    start_date=luigi.DateParameter()
    service_name = luigi.Parameter()

    def requires(self):
        for d in [self.start_date+timedelta(days=x) for x in range((self.end_date-self.start_date).days + 1)]:
            yield InsertDayData(d, self.service_name)

class BackfillLastXDaysData(luigi.Task):
    """Inserts the last X amount of days data into the databse. Helpful for running daily."""
    last_x_days=luigi.IntParameter()
    service_name = luigi.Parameter()

    def requires(self):
        for d in [datetime.now()-timedelta(days=x) for x in range(1, self.last_x_days + 1)]:
            yield InsertDayData(d,self.service_name)
