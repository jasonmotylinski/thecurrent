import config
import redis
import sqlite3
import pandas as pd

from datetime import datetime, timedelta

redis_client = None

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

def get_popular_last_week():
    r=get_redis()
    df=None
    key='popular_last_week.sql'
    if r.exists(key):
        df=pd.read_json(r.get(key).decode())
    else:
        last_week=get_last_week_range()
        end_date=last_week["end_date"]
        start_date=last_week["start_date"]
        t="""
        SELECT artist, title, COUNT(*) as ct
        FROM songs
        WHERE played_at >= '{start_date.year}-{start_date.month:02d}-{start_date.day:02d}T00:00:00.000-06:00'
        AND played_at <= '{end_date.year}-{end_date.month:02d}-{end_date.day:02d}T23:59:59.000-06:00'
        GROUP BY artist, title
        ORDER BY ct DESC
        LIMIT 10
        """.format(start_date=start_date, end_date=end_date)

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
        t="""
        SELECT 
            a.artist, 
            a.title, 
            a.played_at
        FROM songs a
        INNER JOIN (
            SELECT 
                artist, 
                title, 
                played_at, 
                DENSE_RANK() OVER (
                PARTITION BY artist, title
                ORDER BY played_at ASC) AS rank
            FROM songs
            WHERE trim(artist) != ''
            or trim(title) != ''
        ) b
        ON a.artist=b.artist
        AND a.title=b.title
        AND a.played_at=b.played_at
        WHERE  b.rank=1
        AND b.played_at >= '{yesterday.year}-{yesterday.month:02d}-{yesterday.day:02d}T00:00:00.000-06:00'
        AND b.played_at <= '{yesterday.year}-{yesterday.month:02d}-{yesterday.day:02d}T23:59:59.000-06:00'
        ORDER BY a.played_at DESC
        LIMIT 100
        """.format(yesterday=yesterday)

        con = sqlite3.connect(config.DB)
        df=pd.read_sql(t, con)
    return df

def get_popular_all_time_timeseries():
    r=get_redis()
    df=None
    key='popular_all_time_timeseries.sql'
    if r.exists(key):
        df=pd.read_json(r.get(key).decode())
    else:
        t = """
        SELECT 
            artist, 
            year,
            month,
            year || "-" || month AS year_month, 
            COUNT(*) as ct 
        FROM songs 
        WHERE artist IN(
            SELECT artist
            FROM songs 
            GROUP BY artist
            ORDER BY COUNT(*) DESC
            LIMIT 5
        )
        GROUP BY artist, year, month
        ORDER BY year, month ASC
        """
        con = sqlite3.connect(config.DB)
        df=pd.read_sql(t, con)
    return df

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
        t = """SELECT artist, COUNT(*) as ct 
            FROM songs
            {where}
            GROUP BY artist
            ORDER BY ct DESC
            LIMIT 5""".format(where=where)
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
        t="""SELECT 
        artist, 
        COUNT(*) as ct
        FROM songs
        WHERE day_of_week='{day_of_week}'
        AND hour={hour}
        AND artist != ''
        GROUP BY artist
        ORDER BY ct DESC
        LIMIT 5""".format(hour=hour, day_of_week=day_of_week)
        con = sqlite3.connect(config.DB)
        df=pd.read_sql(t, con)
    return df