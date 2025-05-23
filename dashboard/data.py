import config
import logging
import pandas as pd
import redis
import time 
from io import StringIO
from datetime import datetime, timedelta
from sqlalchemy import create_engine

log = logging.getLogger(config.LOGGER_NAME)
redis_client = None
SQL_ROOT ="sql/"

def get_redis():
    """Returns the active redis client. Creates a client if one does not exist

    Returns:
        Redis: The active Redis client
    """
    global redis_client
    if redis_client is None:
        redis_client=redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
    return redis_client

def get_engine():
    """Creates a Postgres engine which can be used by Pandas

    Returns:
        Engine: Postgres engine
    """
    return create_engine(config.DB_PG_CONN)

def get_yesterday():
    """Calculates yesterday's date based on today's UTC

    Returns:
        datetime: yesterday
    """
    return datetime.utcnow() - timedelta(days=1)

def get_last_week_range():
    """Calculates the date range for last week. 

    Returns:
        dict: contains 'start_date' and 'end_date' of last week
    """
    end_date=datetime.utcnow() - timedelta(days=1)
    start_date=datetime.utcnow() - timedelta(days=7)
    return {"start_date": start_date.date(), "end_date": end_date.date()}

def tomorrow_at_105_am_est():
    """Calculates tomorrow at 1:05am eastern time. Used to expire the Redis cache at night.

    Returns:
        int: The datetime as an integer used by Redis to expire the cache at
    """
    tomorrow_utc=datetime.utcnow() + timedelta(days=1)
    dt=datetime(tomorrow_utc.year, tomorrow_utc.month,tomorrow_utc.day, 6, 5)
    return int(time.mktime(dt.timetuple()))

def in_5_minutes():
    """Calculates the time in 5 minutes. Used to expire the Redis cache in 5 minutes.

    Returns:
        int: The datetime as an integer used by Redis to expire the cache at
    """
    dt=datetime.utcnow() + timedelta(minutes=5)
    return int(time.mktime(dt.timetuple()))

def get_sql(filename):
    """Retrieves the given SQL file contains from disk.

    Args:
        filename (string): The file name to retrieve

    Returns:
        string: The contents of the file
    """
    sql_file_path=SQL_ROOT + filename
    with open(sql_file_path) as f:
        sql=f.read()
    return sql

def get_data(filename, cache_expire_at, params={}):
    """Retrieves the requested data from either Redis cache or Postgres. If the data 
       is not in cache it queries the database, puts the data in cache with the given expiration time,
       and returns the data

    Args:
        filename (string): The name of the query file.
        params (dict, optional): A dictionary of parameters used in the SQL statement. Defaults to {}.
        cache_expire_at (_type_): The datetime as an integer to expire the cache at. Defaults to tomorrow_at_105_am_est().

    Returns:
        DataFrame: A dataframe of the data from the query
    """
    r=get_redis()
    
    key=filename + "_".join([str(v) for v in params.values()])

    if not r.exists(key) or config.DEBUG:
        log.info("get_data:INFO:cache miss:key:{0}".format(key))
        t=get_sql(filename) % (params)
        with get_engine().connect() as conn:
            log.info("get_data:INFO:executing SQL:{0}".format(t))
            value=pd.read_sql(t, conn).to_json()
            r.set(key, value, exat=cache_expire_at)
            log.info("get_data:INFO:set key:{0} exat: {1}".format(key, cache_expire_at))
    try:
        log.info("get_data:INFO:reading key from cache:key:{0}".format(key))
        return pd.read_json(StringIO(r.get(key).decode()))
    except Exception as e:
        log.error("get_data:ERROR:key:{0}: {1}".format(key, e))
        return pd.DataFrame([])

def get_last_updated():
    """Gets the date the data was last updated

    Returns:
        datetime: The most recent played_at date for all songs
    """
    filename="last_updated.sql"
    df=get_data(filename,tomorrow_at_105_am_est())
    return df["played_at"].max()

def get_title_timeseries(artist, title, start_date, end_date, service_id=1):

    filename='title_timeseries.sql'
    params={
        "service_id": service_id,
        "artist": artist.replace('\'', '\'\''), 
        "title": title.replace('\'', '\'\''), 
        "start_date": start_date.date(),
        "start_date_week": int(start_date.strftime("%U")), 
        "end_date": end_date.date(), 
        "end_date_week": int(end_date.strftime("%U"))
    }
    
    df=get_data(filename,tomorrow_at_105_am_est(), params)
    df["yw"]=df["yw"].astype("str")
    return df

def get_popular_artist_title_last_week(service_id=1):
    last_week=get_last_week_range()
    filename='popular_artist_title_last_week.sql'
    params={
        "service_id": service_id,
        "last_week": get_last_week_range(),
        "end_date": last_week["end_date"],
        "start_date": last_week["start_date"]
    }
  
    return get_data(filename, tomorrow_at_105_am_est(), params)

def get_popular_artist_last_week(service_id=1):
    last_week=get_last_week_range()
    filename='popular_artist_last_week.sql'
    params={
        "service_id": service_id,
        "end_date": last_week["end_date"],
        "start_date": last_week["start_date"]
    }
    return get_data(filename, tomorrow_at_105_am_est(), params)

def get_popular_all_time_timeseries(service_id):
    params={
        "service_id": service_id
    }
    filename='popular_all_time_timeseries.sql'
    return get_data(filename, tomorrow_at_105_am_est(), params)

def get_popular_all_time(service_id, start_date=None, end_date=None):
    params={
        "service_id": service_id
    }
    filename='popular_all_time.sql'
    return get_data(filename, tomorrow_at_105_am_est(), params)

def get_popular_day_hour_data(SERVICE_ID, hour, day_of_week):
    params={
        "service_id": SERVICE_ID,
        "hour": hour, 
        "day_of_week": day_of_week
    }
    filename='popular_day_hour.sql'
    return get_data(filename, in_5_minutes(), params)


def get_new_last_90_days(service_id=1):
    params={
        "service_id": service_id
    }
    filename='new_last_90_days.sql'
    return get_data(filename,tomorrow_at_105_am_est(), params)
