import config
import requests
from pipelines import BaseSaveDayJsonToLocal

class SaveDayJsonToLocal(BaseSaveDayJsonToLocal):

    def __init__(self, *args, **kwargs):
        super(SaveDayJsonToLocal, self).__init__(*args, **kwargs)
        self.config=config.WFUV

    def get_json(self):
        data={
            'created[min]': self.date,
            'created[max]': self.date,
            'view_name': 'on_air_playlist',
            'view_display_id': 'block_wfuv_on_air_playlist'
        }

        r=requests.post(self.config.URL, data=data)
        return r.json()
    