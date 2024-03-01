import json
import luigi
from hashlib import sha256

def clean_str(str):
    newval= str.replace('"', '""')
    if newval == '':
       return "NULL"
    if newval == 'True':
        newval = 1
    if newval == 'False':
        newval = 0
    return "\"{0}\"".format(newval)

def create_id(played_at, artist, title, source): 
    key = "{0}{1}{2}{3}".format(played_at, artist, title, source)
    m = sha256()
    m.update(key.encode("UTF-8"))
    return m.hexdigest()

class BaseSaveDayJsonToLocal(luigi.Task):
    """Base class for retrieving JSON-based playlist information

    Args:
        luigi (Task): luigi.Task base class

    Raises:
        NotImplementedError: Thrown when the get_json() method is not overwritten by the inheriting class

    Returns:
        BaseSaveDayJsonToLocal: BaseSaveDayJsonToLocal
    """
    date = luigi.DateParameter()
    config = {}

    def output(self):
        """The local output target destination 

        Returns:
            LocalTarget: An object repreenting the output
        """
        return luigi.LocalTarget(self.config.DAY_JSON.format(year=int(self.date.strftime("%Y")), month=int(self.date.strftime("%m")), day=int(self.date.strftime("%d"))))

    def get_json(self):
        """Abstract class for retrieving a JSON-based playlist from the radio station source

        Raises:
            NotImplementedError: Thrown when the inheriting child class does not override this method
        """
        raise NotImplementedError
    
    def run(self):
        """Runs the task by calling get_json() and saving the results to the output()
        """
        with self.output().open('w') as f:
            f.write(json.dumps(self.get_json(), indent=4))