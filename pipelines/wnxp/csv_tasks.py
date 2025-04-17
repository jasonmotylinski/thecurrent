import config
import json
import luigi
from datetime import datetime
from pipelines import create_id, BaseConvertDayJsonToCsv
from pipelines.wnxp.json_tasks import SaveDayJsonToLocal


class ConvertDayJsonToCsv(BaseConvertDayJsonToCsv):
    """Parse the articles from the JSON for the given day."""
    date = luigi.DateParameter()

    def __init__(self, *args, **kwargs):
        super(ConvertDayJsonToCsv, self).__init__(*args, **kwargs)
        self.config= config.WNXP

    def requires(self):
        """Requires."""
        yield SaveDayJsonToLocal(self.date)

    def get_rows(self, input):
        records=json.load(input)["response"]
        for s in records :
            yield [create_id(s["played_at"], s["artist"], s["song"], config.WNXP.SERVICE_ID), 
                    s["artist"],
                    s["song"],
                    '', # album
                    s["played_at"],
                    '', # Duration
                    config.WNXP.SERVICE_ID, # Service ID
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
                    datetime.fromisoformat(s["played_at"]).strftime("%Y"),
                    datetime.fromisoformat(s["played_at"]).strftime("%m"),
                    datetime.fromisoformat(s["played_at"]).strftime("%d"),
                    datetime.fromisoformat(s["played_at"]).strftime("%A"),
                    datetime.fromisoformat(s["played_at"]).strftime("%U"),
                    datetime.fromisoformat(s["played_at"]).strftime("%H")]
