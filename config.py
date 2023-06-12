import os

DEBUG=os.getenv("DEBUG", False)

DB="thecurrent.sqlite3"

DB_MYSQL_HOST=os.getenv("DB_MYSQL_HOST")
DB_MYSQL_USER=os.getenv("DB_MYSQL_USER")
DB_MYSQL_PASSWD=os.getenv("DB_MYSQL_PASSWD")
DB_MYSQL_DB="thecurrent"

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

REDIS_HOST="127.0.0.1"
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL="redis://{host}:{port}/{db}".format(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

MUSICBRAINZ_ARTISTS_JSON="output/musicbrainz/artists.json"
MUSICBRAINZ_RELEASEGROUPS_JSON="output/musicbrainz/releasegroups.json"
MUSICBRAINZ_RELEASEGROUPS_CSV_HEADER_ROW=['id', 'artist', 'title', 'first_release_date']
MUSICBRAINZ_RELEASEGROUPS_CSV="output/musicbrainz/releasegroups.csv"
MUSICBRAINZ_RECORDINGS_JSON="output/musicbrainz/recordings.json"