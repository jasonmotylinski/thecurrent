import config
import json
import luigi
from datetime import datetime
from pipelines import create_id, BaseConvertDayJsonToCsv
from pipelines.kcrw.json_tasks import SaveDayJsonToLocal


class ConvertDayJsonToCsv(BaseConvertDayJsonToCsv):
    """Parse the articles from the JSON for the given day."""
    date = luigi.DateParameter()

    def __init__(self, *args, **kwargs):
        super(ConvertDayJsonToCsv, self).__init__(*args, **kwargs)
        self.config= config.KCRW
    
    def requires(self):
        """Requires."""
        yield SaveDayJsonToLocal(self.date)

    def get_rows(self, input):
        """Run."""
        for s in json.load(input):
            played_at=datetime.fromisoformat(s["datetime"])
            iso_year, iso_week, iso_weekday = played_at.isocalendar()
            yield [ create_id(played_at, s["artist"], s["title"], self.config.SERVICE_ID),
                    s["artist"],
                    s["title"],
                    s["album"],
                    played_at.isoformat(),
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
                    iso_year,
                    played_at.strftime("%m"),
                    played_at.strftime("%d"),
                    played_at.strftime("%A"),
                    iso_week,
                    played_at.strftime("%H")]


