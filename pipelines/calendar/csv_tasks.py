import config
import csv
import luigi
import os

from datetime import datetime, timedelta

class CreateCalendarCsv(luigi.Task):
    """Create CSV file of calendar data."""

    def output(self):
        """Output."""
        return luigi.LocalTarget(config.CALENDAR_CSV)

    def run(self):
        start=datetime(2005,1,1)
        end=datetime(2051,1,1)

        d = os.path.dirname(self.output().path)
        if not os.path.exists(d):
            os.makedirs(d)
        with open(self.output().path, 'w') as f:
            writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
            writer.writerow(config.CALENDAR_HEADER_ROW)

            current=start
            while current < end:
                writer.writerow([
                    current.year,
                    current.month, 
                    current.day, 
                    current.hour, 
                    current.strftime("%A"),
                    current.strftime("%U")
                ])
                current=current + timedelta(hours=1)