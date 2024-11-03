import config
import requests
from pipelines import BaseSaveDayJsonToLocal

class SaveDayJsonToLocal(BaseSaveDayJsonToLocal):
    def __init__(self, *args, **kwargs):
        super(SaveDayJsonToLocal, self).__init__(*args, **kwargs)
        self.config= config.KUOM

    def get_json(self):
        day=[]
        for i in range(0,24):
            r=requests.get(self.config.DAY_URL.format(date=self.date, hour=i))
            day.append(r.json()[0])
        return day

