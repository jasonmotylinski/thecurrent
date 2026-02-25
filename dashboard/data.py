import config
import logging
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta, timezone
from db import get_cache, get_engine

log = logging.getLogger(config.LOGGER_NAME)
SQL_ROOT ="sql/"

def get_yesterday():
    """Calculates yesterday's date based on today's UTC

    Returns:
        datetime: yesterday
    """
    return datetime.now(timezone.utc) - timedelta(days=1)

def get_last_week_range():
    """Calculates the date range for last week. 

    Returns:
        dict: contains 'start_date' and 'end_date' of last week
    """
    end_date=datetime.now(timezone.utc) - timedelta(days=1)
    start_date=datetime.now(timezone.utc) - timedelta(days=7)
    return {"start_date": start_date.date(), "end_date": end_date.date()}

def tomorrow_at_105_am_est():
    """Calculates seconds until tomorrow at 1:05am eastern time. Used to expire the cache at night.

    Returns:
        float: Seconds until expiry
    """
    tomorrow_utc=datetime.now(timezone.utc) + timedelta(days=1)
    dt=datetime(tomorrow_utc.year, tomorrow_utc.month,tomorrow_utc.day, 6, 5, tzinfo=timezone.utc)
    return (dt - datetime.now(timezone.utc)).total_seconds()

def in_5_minutes():
    """Returns 5 minutes in seconds. Used to expire the cache in 5 minutes.

    Returns:
        float: Seconds until expiry
    """
    return timedelta(minutes=5).total_seconds()

def in_30_seconds():
    """Returns 30 seconds. Used for short-lived cache for search queries.

    Returns:
        float: Seconds until expiry
    """
    return 30.0

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

def get_data(filename, cache_expire_secs, params={}):
    """Retrieves the requested data from either disk cache or Postgres. If the data
       is not in cache it queries the database, puts the data in cache with the given expiration time,
       and returns the data

    Args:
        filename (string): The name of the query file.
        params (dict, optional): A dictionary of parameters used in the SQL statement. Defaults to {}.
        cache_expire_secs (float): Seconds until the cache entry expires.

    Returns:
        DataFrame: A dataframe of the data from the query
    """
    cache = get_cache()

    key=filename + "_".join([str(v) for v in params.values()])

    if key not in cache or config.DEBUG:
        log.info(f"get_data:INFO:cache miss:key:{key}")
        t=get_sql(filename) % (params)
        with get_engine().connect() as conn:
            log.info(f"get_data:INFO:executing SQL:{t}")
            value=pd.read_sql(t, conn).to_json()
            cache.set(key, value, expire=cache_expire_secs)
            log.info(f"get_data:INFO:set key:{key} value:{value[:100]} expire_secs:{cache_expire_secs}")
    try:
        log.info(f"get_data:INFO:reading key from cache:key:{key}")
        return pd.read_json(StringIO(cache[key]))
    except Exception as e:
        log.error(f"get_data:ERROR:key:{key}: {e}")
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

def get_artist_titles_from_yesterday():
    yesterday = get_yesterday().date()
    start_date = datetime.combine(yesterday, datetime.min.time())
    end_date = datetime.combine(yesterday, datetime.max.time())
    filename = 'artist_titles_from_yesterday.sql'
    params = {
        "start_date": start_date,
        "end_date": end_date
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

def _execute_sql_with_wildcards(filename, params, cache_expire_secs):
    """Execute SQL that contains ILIKE wildcards (% characters).

    This is needed because psycopg interprets % as format specifiers,
    so we need to double them after Python string formatting.
    """
    cache = get_cache()
    key = filename + "_".join([str(v) for v in params.values()])

    if key not in cache or config.DEBUG:
        log.info(f"_execute_sql_with_wildcards:INFO:cache miss:key:{key}")
        t = get_sql(filename) % params
        # Escape % for psycopg by doubling them (after Python formatting is done)
        t = t.replace('%', '%%')
        with get_engine().connect() as conn:
            log.info(f"_execute_sql_with_wildcards:INFO:executing SQL:{t}")
            value = pd.read_sql(t, conn).to_json()
            cache.set(key, value, expire=cache_expire_secs)
            log.info(f"_execute_sql_with_wildcards:INFO:set key:{key} expire_secs:{cache_expire_secs}")
    try:
        log.info(f"_execute_sql_with_wildcards:INFO:reading key from cache:key:{key}")
        return pd.read_json(StringIO(cache[key]))
    except Exception as e:
        log.error(f"_execute_sql_with_wildcards:ERROR:key:{key}: {e}")
        return pd.DataFrame([])

def search_songs(query):
    """Search for songs by artist or title across all stations.

    Args:
        query (string): The search term

    Returns:
        DataFrame: Matching songs with artist, title, service_id, and total_plays
    """
    filename = 'search.sql'
    search_term = '%' + query.replace("'", "''") + '%'
    params = {"search_term": search_term}
    return _execute_sql_with_wildcards(filename, params, in_30_seconds())

def get_artist_analytics(artist):
    """Get cross-station play analytics for an artist.

    Args:
        artist (string): The artist name

    Returns:
        DataFrame: Monthly play counts by station
    """
    filename = 'artist_analytics.sql'
    params = {
        "artist": artist.replace("'", "''")
    }
    return _execute_sql_with_wildcards(filename, params, tomorrow_at_105_am_est())

def get_artist_top_songs(artist):
    """Get top 5 songs by an artist across all stations.

    Args:
        artist (string): The artist name

    Returns:
        DataFrame: Top 5 songs with play counts
    """
    filename = 'artist_top_songs.sql'
    params = {
        "artist": artist.replace("'", "''")
    }
    return _execute_sql_with_wildcards(filename, params, tomorrow_at_105_am_est())

def get_artist_top_songs_timeseries(artist):
    """Get timeseries play data for an artist's top 5 songs across all stations.

    Args:
        artist (string): The artist name

    Returns:
        DataFrame: Monthly play counts by song and station
    """
    filename = 'artist_top_songs_timeseries.sql'
    params = {
        "artist": artist.replace("'", "''")
    }
    return _execute_sql_with_wildcards(filename, params, tomorrow_at_105_am_est())

def get_song_analytics(artist, title):
    """Get cross-station play analytics for a specific song.

    Args:
        artist (string): The artist name
        title (string): The song title

    Returns:
        DataFrame: Monthly play counts by station
    """
    filename = 'song_analytics.sql'
    params = {
        "artist": artist.replace("'", "''"),
        "title": title.replace("'", "''")
    }
    return _execute_sql_with_wildcards(filename, params, tomorrow_at_105_am_est())

def get_popular_artist_title_timeseries(service_id):
    """Get weekly play timeseries for top 10 popular songs of a station.

    This batches the timeseries data for all top 10 songs in a single query,
    reducing the number of API calls from 10 to 1.

    Args:
        service_id (int): The service/station ID

    Returns:
        DataFrame: Weekly play counts for each top song (artist, title, year, week, ct)
    """
    filename = 'popular_artist_title_timeseries.sql'
    params = {"service_id": service_id}
    return get_data(filename, tomorrow_at_105_am_est(), params)

def get_station_exclusives(service_id):
    """Get artists played exclusively on one station in the last 90 days.

    Args:
        service_id (int): The service/station ID

    Returns:
        DataFrame: Artists exclusive to the station with play counts
    """
    filename = 'station_exclusives.sql'
    params = {"service_id": service_id}
    return get_data(filename, tomorrow_at_105_am_est(), params)

def get_deep_cuts():
    """Get songs with low play counts but played across multiple stations.

    These are quality songs that multiple stations independently choose,
    indicating curator consensus despite low overall play counts.

    Returns:
        DataFrame: Songs played on 4+ stations with low total plays
    """
    filename = 'deep_cuts.sql'
    return get_data(filename, tomorrow_at_105_am_est())

def get_genre_by_hour(service_id):
    """Get genre distribution by hour of day for a station.

    Args:
        service_id (int): The service/station ID

    Returns:
        DataFrame: Play counts by genre and hour
    """
    filename = 'genre_by_hour.sql'
    params = {"service_id": service_id}
    return get_data(filename, tomorrow_at_105_am_est(), params)

def get_station_hidden_gems(service_id):
    """Get songs this station champions that aren't getting play elsewhere.

    Args:
        service_id (int): The service/station ID

    Returns:
        DataFrame: Songs with plays_here >= 3 and plays_elsewhere < 20
    """
    filename = 'station_hidden_gems.sql'
    params = {"service_id": service_id}
    return get_data(filename, tomorrow_at_105_am_est(), params)

def get_top_100_songs_current_year(service_id):
    """Get top 100 songs for current calendar year for a station.

    Args:
        service_id (int): The service/station ID

    Returns:
        DataFrame: Top 100 songs with artist, title, total_plays
    """
    filename = 'top_100_songs_current_year.sql'
    params = {"service_id": service_id}
    return get_data(filename, tomorrow_at_105_am_est(), params)

def get_top_100_songs_timeseries(service_id):
    """Get monthly play timeseries for top 100 songs of current year.

    This batches the timeseries data for all top 100 songs in a single query,
    reducing the number of database queries from 100 to 1.

    Args:
        service_id (int): The service/station ID

    Returns:
        DataFrame: Monthly play counts for each top song (artist, title, month, plays)
    """
    filename = 'top_100_songs_timeseries.sql'
    params = {"service_id": service_id}
    return get_data(filename, tomorrow_at_105_am_est(), params)
