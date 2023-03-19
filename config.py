import os

DB_CONNECTION_URL=os.environ.get("DB_CONNECTION_URL")

CSV_HEADER_ROW = ['id', 'artist', 'title', 'album', 'played_at', 'duration', 'service_id', 'song_id', 'play_id', 
                  'composer', 'conductor', 'orch_ensemble', 'soloist_1', 'soloist_2', 'soloist_3', 'soloist_4',
                  'soloist_5', 'soloist_6', 'record_co', 'record_id', 'addl_text', 'broadcast', 'songs_on_album',
                  'songs_by_artist', 'album_mbid', 'art_url', 'year', 'month', 'day', 'day_of_week', 'week','hour']
HOUR_URL="https://www.thecurrent.org/playlist/{year}-{month:02d}-{day:02d}/{hour:02d}"
DAY_URL="https://www.thecurrent.org/playlist/{year}-{month:02d}-{day:02d}/"
DAY_CSV="output/csv/{0}/{1}/{0}{1}{2}.csv"
YEAR_CSV="output/csv/{0}.csv"
ARTISTS_CSV="output/artists_genres/artists.csv"
ARTISTS_GENRES_JSON="output/artists_genres/artists_genres.json"
EVERYNOISE_URL="https://everynoise.com/lookup.cgi?who={who}&mode=map"
HOUR_HTML="output/html/by_hour/{year}/{month:02d}/{day:02d}/playlist_{year}{month:02d}{day:02d}{hour:02d}.html"
DAY_HTML="output/html/by_day/{year}/{month:02d}/playlist_{year}{month:02d}{day:02d}.html"