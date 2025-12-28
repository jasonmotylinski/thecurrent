import config
import json
import luigi
from parsers.kwss import KwssParser


class SaveDayJsonToLocal(luigi.Task):
    """Save the KWSS songs to JSON locally."""
    date = luigi.DateParameter()

    def __init__(self, *args, **kwargs):
        super(SaveDayJsonToLocal, self).__init__(*args, **kwargs)
        self.config = config.KWSS

    def output(self):
        """The local output target destination

        Returns:
            LocalTarget: An object representing the output
        """
        return luigi.LocalTarget(self.config.DAY_JSON.format(year=self.date.strftime("%Y"), month=int(self.date.strftime("%m")), day=int(self.date.strftime("%d"))))

    def run(self):
        """Runs the task by calling the parser and saving the results to JSON
        """
        parser = KwssParser(self.config)
        songs = list(parser.get_songs(self.date))

        d = self.output().path
        import os
        os.makedirs(os.path.dirname(d), exist_ok=True)

        with self.output().open('w') as f:
            f.write(json.dumps(songs, indent=4))