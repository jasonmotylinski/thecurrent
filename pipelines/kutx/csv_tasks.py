import config
import json
import luigi
from datetime import datetime
from pipelines import create_id, BaseConvertDayJsonToCsv
from pipelines.kutx.json_tasks import SaveDayJsonToLocal


class ConvertDayJsonToCsv(BaseConvertDayJsonToCsv):
    """Parse the articles from the JSON for the given day."""
    date = luigi.DateParameter()

    def __init__(self, *args, **kwargs):
        super(ConvertDayJsonToCsv, self).__init__(*args, **kwargs)
        self.config=config.KUTX

    def requires(self):
        """Requires."""
        yield SaveDayJsonToLocal(self.date)

    def get_rows(self, input):
        """Run."""

        for p in json.load(input)["onToday"]:
                records=p['playlist']
                if records:
                    for s in records:
                        played_at=datetime.strptime(s["_start_time"]+"-06:00", "%m-%d-%Y %H:%M:%S%z") 
                        album=None
                        if 'collectionName' in s:
                            album=s["collectionName"]
                        yield[ create_id(played_at, s["artistName"], s["trackName"], config.KUTX.SERVICE_ID), 
                                s["artistName"],
                                s["trackName"],
                                album,
                                played_at.isoformat(),
                                s["_duration"], # Duration
                                config.KUTX.SERVICE_ID, # Service ID
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
                                played_at.strftime("%Y"),
                                played_at.strftime("%m"),
                                played_at.strftime("%d"),
                                played_at.strftime("%A"),
                                played_at.strftime("%U"),
                                played_at.strftime("%H")]
