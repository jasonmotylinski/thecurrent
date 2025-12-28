import config
import json
import luigi
from parsers.kwss import KwssParser
from pipelines import create_id, BaseConvertDayJsonToCsv
from datetime import datetime
from pipelines.kwss.json_tasks import SaveDayJsonToLocal


class ConvertDayJsonToCsv(BaseConvertDayJsonToCsv):
    """Parse the songs from the JSON for the given day."""
    date = luigi.DateParameter()

    def __init__(self, *args, **kwargs):
        super(ConvertDayJsonToCsv, self).__init__(*args, **kwargs)
        self.config = config.KWSS

    def requires(self):
        """Requires."""
        yield SaveDayJsonToLocal(self.date)
        
    def get_rows(self, input):
        records = json.load(input)
        for song in records:
            # Parse played_at to datetime for extracting date components
            played_at_dt = datetime.fromisoformat(song['played_at'])
            yield [
                create_id(song['played_at'], song['artist'], song['song'], self.config.SERVICE_ID),
                song['artist'],
                song['song'],
                song.get('album', ''),
                song['played_at'],
                '',  # Duration
                self.config.SERVICE_ID,
                '',  # song_id
                '',  # play_id
                '',  # composer
                '',  # conductor
                '',  # orch_ensemble
                '',  # soloist_1
                '',  # soloist_2
                '',  # soloist_3
                '',  # soloist_4
                '',  # soloist_5
                '',  # soloist_6
                '',  # record_co
                '',  # record_id
                '',  # addl_text
                '',  # broadcast
                '',  # songs_on_album
                '',  # songs_by_artist
                '',  # album_mbid
                '',  # art_url
                played_at_dt.strftime("%Y"),
                played_at_dt.strftime("%m"),
                played_at_dt.strftime("%d"),
                played_at_dt.strftime("%w"),  # day_of_week (0=Sunday)
                played_at_dt.strftime("%U"),  # week
                played_at_dt.strftime("%H")   # hour
            ]