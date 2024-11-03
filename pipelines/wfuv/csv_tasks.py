import config
import json
import luigi
from parsers.wfuv import WfuvParser
from pipelines import create_id, BaseConvertDayJsonToCsv
from pipelines.wfuv.json_tasks import SaveDayJsonToLocal


class ConvertDayJsonToCsv(BaseConvertDayJsonToCsv):
    """Parse the articles from the JSON for the given day."""
    date = luigi.DateParameter()

    def __init__(self, *args, **kwargs):
        super(ConvertDayJsonToCsv, self).__init__(*args, **kwargs)
        self.config= config.WFUV

    def requires(self):
        """Requires."""
        yield SaveDayJsonToLocal(self.date)
        
    def get_rows(self, input):
        parser=WfuvParser(self.config)

        for song in parser.get_songs(input):
            yield [create_id(song['played_at'], song['artist'], song['song'], self.config.SERVICE_ID), 
                    song['artist'],
                    song['song'],
                    '',
                    song['played_at'].isoformat(),
                    '', # Duration
                    self.config.SERVICE_ID, # Service ID
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    song['played_at'].strftime("%Y"),
                    song['played_at'].strftime("%m"),
                    song['played_at'].strftime("%d"),
                    song['played_at'].strftime("%A"),
                    song['played_at'].strftime("%U"),
                    song['played_at'].strftime("%H")]
        

