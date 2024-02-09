import config
import json
import luigi
import requests


class SaveDayJsonToLocal(luigi.Task):
    """Get an hour of playlist."""
    date = luigi.DateParameter()

    def output(self):
        """Output."""
        return luigi.LocalTarget(config.WFUV.DAY_JSON.format(year=int(self.date.strftime("%Y")), month=int(self.date.strftime("%m")), day=int(self.date.strftime("%d"))))

    def run(self):
        """Run."""
        with self.output().open('w') as f:

            data={
                'created[min]': self.date,
                'created[max]': self.date,
                'view_name': 'on_air_playlist',
                'view_display_id': 'block_wfuv_on_air_playlist'
            }

            r=requests.post(config.WFUV.URL, data=data)

            f.write(json.dumps(r.json(), indent=4))