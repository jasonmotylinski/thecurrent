import os
from dotenv import load_dotenv

load_dotenv()


DEBUG=os.getenv("DEBUG", False)
LOGGER_NAME=os.getenv("LOGGER_NAME", "root")
DB="thecurrent.sqlite3"

DB_MYSQL_HOST=os.getenv("DB_MYSQL_HOST")
DB_MYSQL_USER=os.getenv("DB_MYSQL_USER")
DB_MYSQL_PASSWD=os.getenv("DB_MYSQL_PASSWD")
DB_PG_HOST=os.getenv("DB_PG_HOST")
DB_PG_USER=os.getenv("DB_PG_USER")
DB_PG_PASSWD=os.getenv("DB_PG_PASSWD")
DB_NAME="thecurrent"
DB_MYSQL_CONN="mysql://{1}:{2}@{0}/{3}".format(DB_MYSQL_HOST, DB_MYSQL_USER, DB_MYSQL_PASSWD, DB_NAME)
DB_PG_CONN="postgresql+psycopg://{1}:{2}@{0}/{3}".format(DB_PG_HOST, DB_PG_USER, DB_PG_PASSWD, DB_NAME)

CSV_HEADER_ROW = ['id', 'artist', 'title', 'album', 'played_at', 'duration', 'service_id', 'song_id', 'play_id', 
                  'composer', 'conductor', 'orch_ensemble', 'soloist_1', 'soloist_2', 'soloist_3', 'soloist_4',
                  'soloist_5', 'soloist_6', 'record_co', 'record_id', 'addl_text', 'broadcast', 'songs_on_album',
                  'songs_by_artist', 'album_mbid', 'art_url', 'year', 'month', 'day', 'day_of_week','week','hour']
CALENDAR_HEADER_ROW= ['year','month', 'day','hour','day_of_week','day_of_week_int', 'week_of_year']
CALENDAR_CSV="output/calendar/calendar.csv"


THECURRENT_HOUR_URL="https://www.thecurrent.org/playlist/{year}-{month:02d}-{day:02d}/{hour:02d}"
THECURRENT_DAY_URL="https://www.thecurrent.org/playlist/{year}-{month:02d}-{day:02d}/"
THECURRENT_SCHEDULE_DAY_URL="https://www.thecurrent.org/schedule/the-current/{date.year}-{date.month}-{date.day}"
THECURRENT_DAY_CSV="output/thecurrent/csv/{0}/{1}/{2}.csv"
THECURRENT_YEAR_CSV="output/thecurrent/csv/{0}.csv"
THECURRENT_HOUR_HTML="output/thecurrent/html/by_hour/{year}/{month:02d}/{day:02d}/playlist_{year}{month:02d}{day:02d}{hour:02d}.html"
THECURRENT_DAY_HTML="output/thecurrent/html/by_day/{year}/{month:02d}/playlist_{year}{month:02d}{day:02d}.html"
THECURRENT_SCHEDULE_DAY_HTML="output/thecurrent/schedule/html/by_day/{year}/{month:02d}/{year}{month:02d}{day:02d}.html"
THECURRENT_SCHEDULE_DAY_CSV="output/thecurrent/schedule/csv/{0}/{1}/{2}.csv"
THECURRENT_ARTISTS_CSV="output/thecurrent/artists.csv"
THECURRENT_SCHDEULE_YEAR_CSV="output/thecurrent/schedule/csv/{0}.csv"
THECURRENT_SCHEDULE_CSV_HEADER_ROW =['id', 'show_id', 'host_name', 'show_name', 'start_time', 'end_time']

EVERYNOISE_ARTISTS_GENRES_CSV="output/everynoise/artists_genres.csv"
EVERYNOISE_ARTISTS_GENRES_JSON="output/everynoise/artists_genres.json"
EVERYNOISE_URL="https://everynoise.com/lookup.cgi?who={who}&mode=map"
EVERYNOISE_CSV_HEADER_ROW=['artist', 'genre', 'source']

WIKIPEDIA_ARTISTS_JSON="output/wikipedia/artists_wikipedia.json"
WIKIPEDIA_URL="https://en.wikipedia.org/wiki/{artist}"
WIKIPEDIA_BAND_URL="https://en.wikipedia.org/wiki/{artist}_(band)"
WIKIPEDIA_MUSICIAN_URL="https://en.wikipedia.org/wiki/{artist}_(musician)"
WIKIPEDIA_MUSIC_GROUP_URL="https://en.wikipedia.org/wiki/{artist}_(music_group)"

WIKIPEDIA_URLS ={
    "bio": WIKIPEDIA_URL, 
    "band": WIKIPEDIA_BAND_URL,
    "musician": WIKIPEDIA_MUSICIAN_URL,
    "music group": WIKIPEDIA_MUSIC_GROUP_URL
}

DISCOGS_URL="https://www.discogs.com/search/ac?searchType=artist&q={artist}&type=a_m_r_13"
DISCOGS_ARTISTS_JSON="output/discogs/artists_discogs.json"

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL="redis://{host}:{port}/{db}".format(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

MUSICBRAINZ_ARTISTS_JSON="output/musicbrainz/artists.json"
MUSICBRAINZ_RELEASEGROUPS_JSON="output/musicbrainz/releasegroups.json"
MUSICBRAINZ_RELEASEGROUPS_CSV_HEADER_ROW=['id', 'artist', 'title', 'first_release_date']
MUSICBRAINZ_RELEASEGROUPS_CSV="output/musicbrainz/releasegroups.csv"
MUSICBRAINZ_RECORDINGS_JSON="output/musicbrainz/recordings.json"

SPOTIFY_ARTISTS_JSON="output/spotify/artists.json"

class KEXP(object):
    DAY_URL="https://api.kexp.org/v2/plays/?limit=1000&airdate_after={date.year}-{date.month:02d}-{date.day:02d}T00:00:00&airdate_before={date.year}-{date.month:02d}-{date.day:02d}T23:59:59"
    DAY_JSON="output/kexp/json/by_day/{year}/{month:02d}/playlist_{year}{month:02d}{day:02d}.json"
    DAY_CSV="output/kexp/csv/{0}/{1}/{2}.csv"
    SERVICE_ID=2
    SERVICE_NAME="kexp"
    LOGO="/assets/kexp.svg"
    TITLE="90.3 KEXP Trends"
    PATH="/" + SERVICE_NAME
    TOP_10_PLAYLIST="https://open.spotify.com/playlist/1oatZdfsBNYNuUhnNTXXnn"


class KUTX(object):
    DAY_URL="https://api.composer.nprstations.org/v1/widget/50ef24ebe1c8a1369593d032/day?date={date.year}-{date.month:02d}-{date.day:02d}&format=json"
    DAY_JSON="output/kutx/json/by_day/{year}/{month:02d}/playlist_{year}{month:02d}{day:02d}.json"
    DAY_CSV="output/kutx/csv/{0}/{1}/{2}.csv"
    SERVICE_ID=3
    SERVICE_NAME="kutx"
    LOGO="/assets/kutx.svg"
    TITLE="98.9 KUTX Trends"
    PATH="/" + SERVICE_NAME
    TOP_10_PLAYLIST="https://open.spotify.com/playlist/2Rk9whZHSuQ3NgkNYz1mgZ"

class WXPN(object):
    DAY_URL="https://origin.xpn.org/utils/playlist/json/{date.year}-{date.month:02d}-{date.day:02d}.json"
    DAY_JSON="output/wxpn/json/by_day/{year}/{month:02d}/playlist_{year}{month:02d}{day:02d}.json"
    DAY_CSV="output/wxpn/csv/{0}/{1}/{2}.csv"
    SERVICE_ID=4
    SERVICE_NAME="wxpn"
    LOGO="/assets/wxpn.png"
    TITLE="88.5 WXPN Trends"
    PATH="/" + SERVICE_NAME
    TOP_10_PLAYLIST="https://open.spotify.com/playlist/3HGci9o2R4x46L5t0YTNGr"

class THECURRENT(object):
    TITLE="89.3 The Current Trends"
    SERVICE_ID=1
    SERVICE_NAME="kcmp"
    LOGO="/assets/kcmp.svg"
    PATH="/" + SERVICE_NAME
    TOP_10_PLAYLIST="https://open.spotify.com/playlist/0oq9XIzdeGLd90DU2rYxuD"

class WFUV(object):
    SERVICE_ID=5
    SERVICE_NAME="wfuv"
    DAY_JSON="output/wfuv/json/by_day/{year}/{month:02d}/playlist_{year}{month:02d}{day:02d}.json"
    URL="https://wfuv.org/views/ajax?created[min]={date}&created[max]={date}&view_name=on_air_playlist&view_display_id=block_wfuv_on_air_playlist"
    DAY_CSV="output/wfuv/csv/{0}/{1}/{2}.csv"
    LOGO="/assets/wfuv.png"
    TITLE="90.7 WFUV Trends"
    PATH="/" + SERVICE_NAME
    TOP_10_PLAYLIST="https://open.spotify.com/playlist/1SZMsixhwCY0iAyp4FBYHK"

class KCRW(object):
    SERVICE_ID=6
    SERVICE_NAME="kcrw"
    DAY_JSON="output/kcrw/json/by_day/{year}/{month:02d}/playlist_{year}{month:02d}{day:02d}.json"
    DAY_URL="https://tracklist-api.kcrw.com/Simulcast/date/{date.year}/{date.month:02d}/{date.day:02d}?page_size=2000"
    DAY_CSV="output/kcrw/csv/{0}/{1}/{2}.csv"
    TITLE="89.9 KCRW Trends"
    LOGO="/assets/KCRW_Logo_White.png"
    PATH="/" + SERVICE_NAME
    TOP_10_PLAYLIST="https://open.spotify.com/playlist/35d08JaVDjHG8aZMSQx6FE"

class KUOM(object):
    SERVICE_ID=7
    SERVICE_NAME="kuom"
    DAY_JSON="output/kuom/json/by_day/{year}/{month:02d}/playlist_{year}{month:02d}{day:02d}.json"
    DAY_URL="https://radiok.org/playlist-group/{date.year}-{date.month:02d}-{date.day:02d}T{hour:02d}:00:01/{date.year}-{date.month:02d}-{date.day:02d}T{hour:02d}:59?_wrapper_format=drupal_ajax"
    DAY_CSV="output/kuom/csv/{0}/{1}/{2}.csv"
    TITLE="770AM KUOM Trends"
    LOGO="/assets/radiok.svg"
    PATH="/" + SERVICE_NAME
    TOP_10_PLAYLIST="https://open.spotify.com/playlist/3E8BsxdRjfe25XHo51ss2P"

class KKXT(object):
    DAY_URL="https://kkxt.tunegenie.com/api/v1/brand/nowplaying/"
    DAY_JSON="output/kkxt/json/by_day/{year}/{month:02d}/playlist_{year}{month:02d}{day:02d}.json"
    DAY_CSV="output/kkxt/csv/{0}/{1}/{2}.csv"
    SERVICE_ID=8
    SERVICE_NAME="kkxt"
    LOGO="/assets/kkxt.svg"
    TITLE="91.7 KKXT Trends"

class WEHM(object):
    DAY_URL="https://wehm.tunegenie.com/api/v1/brand/nowplaying/"
    DAY_JSON="output/wehm/json/by_day/{year}/{month:02d}/playlist_{year}{month:02d}{day:02d}.json"
    DAY_CSV="output/wehm/csv/{0}/{1}/{2}.csv"
    SERVICE_ID=9
    SERVICE_NAME="wehm"
    LOGO="/assets/wehm.png"
    TITLE="92.9 & 96.9 WEHM Trends"

class WNXP(object):
    DAY_URL="https://wnxp.tunegenie.com/api/v1/brand/nowplaying/"
    DAY_JSON="output/wnxp/json/by_day/{year}/{month:02d}/playlist_{year}{month:02d}{day:02d}.json"
    DAY_CSV="output/wnxp/csv/{0}/{1}/{2}.csv"
    SERVICE_ID=10
    SERVICE_NAME="wnxp"
    LOGO="/assets/wnxp.png"
    TITLE="91.1 WNXP Trends"

class WYEP(object):
    DAY_URL="https://api.composer.nprstations.org/v1/widget/50e451b6a93e91ee0a00028e/day?date={date.year}-{date.month:02d}-{date.day:02d}&format=json"
    DAY_JSON="output/wyep/json/by_day/{year}/{month:02d}/playlist_{year}{month:02d}{day:02d}.json"
    DAY_CSV="output/wyep/csv/{0}/{1}/{2}.csv"
    SERVICE_ID=11
    SERVICE_NAME="wyep"
    LOGO="/assets/wyep.png"
    TITLE="91.3 WYEP Trends"
SERVICES={
    "kexp": KEXP,
    "kutx": KUTX,
    "wxpn": WXPN,
    "kcmp": THECURRENT,
    "wfuv": WFUV,
    "kcrw": KCRW,
    "kuom": KUOM,
    "kkxt": KKXT,
    "wehm": WEHM,
    "wnxp": WNXP
}