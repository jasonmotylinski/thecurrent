import config
import redis
import sqlite3
import pandas as pd

from datetime import datetime, timedelta

redis_client = None
SQL_ROOT ="sql/"

def get_redis():
    global redis_client
    if redis_client is None:
        redis_client=redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
    return redis_client

def get_yesterday():
    return datetime.utcnow() - timedelta(days=1)

def get_last_week_range():
    end_date=datetime.utcnow() - timedelta(days=1)
    start_date=datetime.utcnow() - timedelta(days=7)
    return {"start_date": start_date, "end_date": end_date}

def tomorrow_at_105_am_cst_in_utc():
    tomorrow_utc=datetime.utcnow() + timedelta(days=1)
    return datetime(tomorrow_utc.year, tomorrow_utc.month,tomorrow_utc.day, 6, 5)

def in_5_minutes():
    return datetime.utcnow() + timedelta(minutes=5)

def get_sql(filename):
    sql_file_path=SQL_ROOT + filename
    with open(sql_file_path) as f:
        sql=f.read()
    return sql


def get_title_timeseries(artist, title, start_date, end_date):
    r=get_redis()
    filename='title_timeseries.sql'
    key=filename+ "_"+artist+title+start_date.strftime("%Y%m%d")+end_date.strftime("%Y%m%d")
    
    if not r.exists(key):
        t=get_sql(filename).format(artist=artist, title=title, start_date=start_date, start_date_week=int(start_date.strftime("%U")), end_date=end_date, end_date_week=int(end_date.strftime("%U")))
        con = sqlite3.connect(config.DB)
        value=pd.read_sql(t, con).to_json()
        r.set(key, value, exat=tomorrow_at_105_am_cst_in_utc())
    
    df=pd.read_json(r.get(key).decode())
    df["ymw"]=df["ymw"].astype("str")
    return df
 

def get_popular_artist_title_last_week():
    r=get_redis()
    key='popular_artist_title_last_week.sql'

    if not r.exists(key):
        last_week=get_last_week_range()
        end_date=last_week["end_date"]
        start_date=last_week["start_date"]
        t=get_sql(key).format(start_date=start_date, end_date=end_date)

        con = sqlite3.connect(config.DB)
        value=pd.read_sql(t, con).to_json()
        r.set(key, value, exat=tomorrow_at_105_am_cst_in_utc())

    return pd.read_json(r.get(key).decode())
   

def get_popular_artist_last_week():
    r=get_redis()
    df=None
    key='popular_artist_last_week.sql'
    if r.exists(key):
        df=pd.read_json(r.get(key).decode())
    else:
        last_week=get_last_week_range()
        end_date=last_week["end_date"]
        start_date=last_week["start_date"]
        t=get_sql(key).format(start_date=start_date, end_date=end_date)

        con = sqlite3.connect(config.DB)
        df=pd.read_sql(t, con)
    return df

def get_new_yesterday():

    r=get_redis()
    df=None
    key='new_yesterday.sql'
    if r.exists(key):
        df=pd.read_json(r.get(key).decode())
    else:
        yesterday=get_yesterday()
        t=get_sql(key).format(yesterday=yesterday)

        con = sqlite3.connect(config.DB)
        df=pd.read_sql(t, con)
    return df

def get_popular_all_time_timeseries():
    r=get_redis()
    
    key='popular_all_time_timeseries.sql'
    if not r.exists(key):
        t = get_sql(key)
        con = sqlite3.connect(config.DB)
        value=pd.read_sql(t, con).to_json()
        r.set(key, value, exat=tomorrow_at_105_am_cst_in_utc())

    return pd.read_json(r.get(key).decode())

def get_popular_all_time(start_date=None, end_date=None):

    r=get_redis()
    df=None
    key='popular_all_time.sql'
    if r.exists(key):
        df=pd.read_json(r.get(key).decode())
    else:
        where=""
        if start_date and end_date:
            where="WHERE played_at >='{0}' AND played_at <='{1}'".format(start_date, end_date)
        t = get_sql(key).format(where=where)
        con = sqlite3.connect(config.DB)
        df=pd.read_sql(t, con)
    return df

def get_popular_day_hour_data(hour, day_of_week):
    r=get_redis()
    df=None
    key='popular_day_hour.sql'
    if r.exists(key):
        df=pd.read_json(r.get(key).decode())
    else:
        t=get_sql(key).format(hour=hour, day_of_week=day_of_week)
        con = sqlite3.connect(config.DB)
        df=pd.read_sql(t, con)
    return df

def get_new_last_90_days():
    r=get_redis()

    key='new_last_90_days.sql'
    if not r.exists(key):
        t=get_sql(key)
        con = sqlite3.connect(config.DB)
        value=pd.read_sql(t, con).to_json()
        r.set(key, value, exat=tomorrow_at_105_am_cst_in_utc())

    return pd.read_json(r.get(key).decode())