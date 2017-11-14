from datetime import datetime, timedelta
import dateutil.parser
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

def cleanup():
    to_remove = []
    tracks = spotify.get_playlist_tracks(USER,PLAYLIST)

    for idx,item in enumerate(tracks['items']):
        d = dateutil.parser.parse(item['added_at']).replace(tzinfo=None)
        now = datetime.utcnow().replace(tzinfo=None)
        diff = now - d

        if diff.seconds > 60 * 60:
            to_remove.append({'uri': item['track']['uri'], 'positions': [idx]})
                #(24*60*60) - diff.seconds
        
    if len(to_remove) > 0:
        spotify.remove_tracks(USER, PLAYLIST, to_remove)

start = datetime.now()
uris = []
for i in range(1,3):
    cur = start + timedelta(hours=-i)
    print cur
    tracks = list(playlist.get_hour(cur.year, cur.month, cur.day, cur.hour))
    for track in tracks:
        match = spotify.get_track(track.artist, track.title)
        if len(match['tracks']['items']) == 1:
            uris.append(match['tracks']['items'][0]['uri'])
        else:
            print "unable to find artist: {0} title: {1}".format(track.artist, track.title)

playlist_tracks = spotify.get_playlist_tracks(USER, PLAYLIST)

most_recent_uri = playlist_tracks['items'][0]['track']['uri']
try:
    max = uris.index(most_recent_uri)
except:
    max = len(uris)
    
if max > 0:
    spotify.add_tracks(USER, PLAYLIST, uris[0:max], position=0)
cleanup()

