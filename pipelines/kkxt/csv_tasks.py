import config
import json
import luigi
from datetime import datetime
from pipelines import create_id, BaseConvertDayJsonToCsv
from pipelines.kexp.json_tasks import SaveDayJsonToLocal


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
        records=json.load(input)["results"]
        for s in records :
            if s["play_type"]=="trackplay":
                yield [create_id(s["airdate"], s["artist"], s["song"], config.KKXT.SERVICE_ID), 
                        s["artist"],
                        s["song"],
                        s["album"],
                        s["airdate"],
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
                        datetime.fromisoformat(s["airdate"]).strftime("%Y"),
                        datetime.fromisoformat(s["airdate"]).strftime("%m"),
                        datetime.fromisoformat(s["airdate"]).strftime("%d"),
                        datetime.fromisoformat(s["airdate"]).strftime("%A"),
                        datetime.fromisoformat(s["airdate"]).strftime("%U"),
                        datetime.fromisoformat(s["airdate"]).strftime("%H")]
