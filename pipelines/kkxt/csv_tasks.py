import config
import json
import luigi
from datetime import datetime
from pipelines import create_id, BaseConvertDayJsonToCsv
from pipelines.kkxt.json_tasks import SaveDayJsonToLocal


class ConvertDayJsonToCsv(BaseConvertDayJsonToCsv):
    """Parse the articles from the JSON for the given day."""
    date = luigi.DateParameter()

    def __init__(self, *args, **kwargs):
        super(ConvertDayJsonToCsv, self).__init__(*args, **kwargs)
        self.config= config.KKXT

    def requires(self):
        """Requires."""
        yield SaveDayJsonToLocal(self.date)

    def get_rows(self, input):
        records=json.load(input)["response"]
        for s in records :
            played_at_dt = datetime.fromisoformat(s["played_at"])
            iso_year, iso_week, iso_weekday = played_at_dt.isocalendar()
            yield [create_id(s["played_at"], s["artist"], s["song"], config.KKXT.SERVICE_ID),
                    s["artist"],
                    s["song"],
                    '', # album
                    s["played_at"],
                    '', # Duration
                    config.KKXT.SERVICE_ID, # Service ID
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
                    played_at_dt.strftime("%m"),
                    played_at_dt.strftime("%d"),
                    played_at_dt.strftime("%A"),
                    iso_week,
                    played_at_dt.strftime("%H")]