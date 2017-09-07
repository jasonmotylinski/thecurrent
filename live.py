from datetime import datetime, timedelta
import playlist
import spotify


USER = '12140608440'
PLAYLIST = '1IrKvuJcHtUHaOFZNsoRe8'
MAX_HOURS_AGO = 8
start = datetime.now()

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


uris = []
for i in range(1, MAX_HOURS_AGO):
    cur = start - timedelta(hours=i)
    print cur
    tracks = list(playlist.get_hour(cur.year, cur.month, cur.day, cur.hour))

    for track in tracks:
        match = spotify.get_track(track.artist, track.title)
        if len(match['tracks']['items']) == 1:
            uris.append(match['tracks']['items'][0]['uri'])
playlist = spotify.get_playlist(USER, PLAYLIST)['tracks']['items']

spotify.replace_tracks(USER, PLAYLIST, uris)
