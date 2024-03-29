import luigi
import config
import os
import pandas as pd
import sqlite3
import time

from datetime import datetime, timedelta
from luigi.contrib.redis_store import RedisTarget

SQL_ROOT="sql/"
def tomorrow_at_105_am_cst_in_utc():
    tomorrow_utc=datetime.utcnow() + timedelta(days=1)
    return datetime(tomorrow_utc.year, tomorrow_utc.month,tomorrow_utc.day, 6, 5)

def in_5_minutes():
    return datetime.utcnow() + timedelta(minutes=5)

def get_last_week_range():
    end_date=datetime.utcnow() - timedelta(days=1)
    start_date=datetime.utcnow() - timedelta(days=7)
    return {"start_date": start_date, "end_date": end_date}

def get_yesterday():
    return datetime.utcnow() - timedelta(days=1)

class UpdateCache(luigi.Task):
    sql_file_path=luigi.PathParameter()
    exat=luigi.IntParameter()
    update_id=None


    def output(self):
        self.update_id=os.path.basename(self.sql_file_path)
        return RedisTarget(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, update_id=self.update_id)
    
    def inject_variables(self, sql):
        return sql

    def run(self):
        if not self.exists():
      
            with open(self.sql_file_path) as f:
                sql=f.read()

            sql=self.inject_variables(sql)
            print(sql)
            con = sqlite3.connect(config.DB)
            value=pd.read_sql(sql, con).to_json()
            
            self.output().redis_client.set(self.update_id,value,exat=self.exat)

    def exists(self):
        return self.output().redis_client.exists(self.update_id) == 1

class UpdatePopularAllTimeCache(UpdateCache):
    sql_file_path=luigi.Parameter(default=SQL_ROOT + "popular_all_time.sql")
    exat=luigi.IntParameter(default=int(time.mktime(tomorrow_at_105_am_cst_in_utc().timetuple())))

class UpdatePopularAllTimeTimeseriesCache(UpdateCache):
    sql_file_path=luigi.Parameter(default=SQL_ROOT + "popular_all_time_timeseries.sql")
    exat=luigi.IntParameter(default=int(time.mktime(tomorrow_at_105_am_cst_in_utc().timetuple())))

class UpdatePopularArtistLastWeekCache(UpdateCache):
    sql_file_path=luigi.Parameter(default=SQL_ROOT + "popular_artist_last_week.sql")
    exat=luigi.IntParameter(default=int(time.mktime(tomorrow_at_105_am_cst_in_utc().timetuple())))

    def inject_variables(self, sql):
        last_week=get_last_week_range()
        end_date=last_week["end_date"]
        start_date=last_week["start_date"]
        return sql.format(start_date=start_date, end_date=end_date)

class UpdatePopularArtistTitleLastWeekCache(UpdateCache):
    sql_file_path=luigi.Parameter(default=SQL_ROOT + "popular_artist_title_last_week.sql")
    exat=luigi.IntParameter(default=int(time.mktime(tomorrow_at_105_am_cst_in_utc().timetuple())))

    def inject_variables(self, sql):
        last_week=get_last_week_range()
        end_date=last_week["end_date"]
        start_date=last_week["start_date"]
        return sql.format(start_date=start_date, end_date=end_date)

class UpdateNewYesterdayCache(UpdateCache):
    sql_file_path=luigi.Parameter(default=SQL_ROOT + "new_yesterday.sql")
    exat=luigi.IntParameter(default=int(time.mktime(tomorrow_at_105_am_cst_in_utc().timetuple())))

    def inject_variables(self, sql):
        yesterday=get_yesterday()
        return sql.format(yesterday=yesterday)
    
class UpdatePopularDayHourCache(UpdateCache):
    sql_file_path=luigi.Parameter(default=SQL_ROOT + "popular_day_hour.sql")
    exat=luigi.IntParameter(default=int(time.mktime(in_5_minutes().timetuple())))

    def inject_variables(self, sql):
        hour=datetime.utcnow().hour
        day_of_week=datetime.utcnow().strftime("%A")
        return sql.format(hour=hour, day_of_week=day_of_week)


class UpdateAllCache(luigi.WrapperTask):

    def requires(self):
        yield UpdatePopularAllTimeCache()
        yield UpdatePopularAllTimeTimeseriesCache()
        yield UpdatePopularArtistTitleLastWeekCache()
        yield UpdatePopularArtistLastWeekCache()
        yield UpdateNewYesterdayCache()
        yield UpdatePopularDayHourCache()
