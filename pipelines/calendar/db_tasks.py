import config
import luigi
import sqlite3

from datetime import datetime, timedelta

class InsertCalendarDayData(luigi.Task):
    day_hour=luigi.DateHourParameter()
   
    def run(self):
        t = """
            SELECT *
            FROM calendar
            WHERE 
                year={year}
                AND month={month}
                AND day={day}
                AND hour={hour}
            LIMIT 1""".format(year=self.day_hour.year,month=self.day_hour.month, day=self.day_hour.day, hour=self.day_hour.hour)
        con = sqlite3.connect(config.DB)
        results=con.execute(t).fetchall()

        if(len(results))==0:
            t="""
            INSERT INTO calendar
            VALUES({year}, {month}, {day}, {hour},'{day_of_week}',{week_of_year})
            """.format(year=self.day_hour.year,
                    month=self.day_hour.month, 
                    day=self.day_hour.day, 
                    hour=self.day_hour.hour, 
                    day_of_week=self.day_hour.strftime("%A"),
                    week_of_year=self.day_hour.strftime("%U"))
            con.execute(t)
            con.commit()
    
class InsertAllCalendarData(luigi.Task):
    
    def requires(self):
        start=datetime(2005,1,1)
        end=datetime(2006,1,1)

        current=start
        while current < end:
            yield InsertCalendarDayData(day_hour=current)
            current=current + timedelta(hours=1)
                