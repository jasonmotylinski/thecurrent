import config
import json
import luigi
from datetime import datetime
from pipelines import create_id, BaseConvertDayJsonToCsv
from pipelines.wxpn.json_tasks import SaveDayJsonToLocal


class ConvertDayJsonToCsv(BaseConvertDayJsonToCsv):
    """Parse the articles from the JSON for the given day."""
    date = luigi.DateParameter()

    def __init__(self, *args, **kwargs):
        super(ConvertDayJsonToCsv, self).__init__(*args, **kwargs)
        self.config= config.WXPN
    
    def requires(self):
        """Requires."""
        yield SaveDayJsonToLocal(self.date)

    def get_rows(self, input):
        """Run."""
        for s in json.load(input):
            if "timeslice" in s:
                played_at=s['timeslice']
            if "air_date" in s:
                played_at=s['air_date']
            played_at=datetime.strptime(played_at+"-05:00", "%Y-%m-%d %H:%M:%S%z") 
            yield [ create_id(played_at, s["artist"], s["song"], config.WXPN.SERVICE_ID), 
                    s["artist"],
                    s["song"],
                    s["album"],
                    played_at.isoformat(),
                    '', # Duration
                    config.WXPN.SERVICE_ID, # Service ID
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


