import config
import requests
from pipelines import BaseSaveDayJsonToLocal

class SaveDayJsonToLocal(BaseSaveDayJsonToLocal):

    def __init__(self, *args, **kwargs):
        super(SaveDayJsonToLocal, self).__init__(*args, **kwargs)
        self.config= config.WXPN

    def get_json(self):
        """Run."""
        r=requests.get(self.config.DAY_URL.format(date=self.date))
        return r.json()