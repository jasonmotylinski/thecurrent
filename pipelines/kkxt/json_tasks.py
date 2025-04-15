import config
import requests
from pipelines import BaseSaveDayJsonToLocal

class SaveDayJsonToLocal(BaseSaveDayJsonToLocal):
    def __init__(self, *args, **kwargs):
        super(SaveDayJsonToLocal, self).__init__(*args, **kwargs)
        self.config= config.KKXT

    def get_json(self):

        headers = {
            'Referer': 'https://kkxt.tunegenie.com/onair/{date}/',
        }

        params = {
            'hour': '16',
            'since': '{date}T00:00:00-05:00'.format(date=self.date),
            'until': '{date}T23:59:59-05:00'.format(date=self.date)
        }

        r=requests.get(self.config.DAY_URL.format(date=self.date), headers=headers, params=params)
        return r.json()