from datetime import datetime

class BaseParser(object):
    _date=datetime.now()
    _config=None

    def __init__(self, config):
        self._config=config

    def parse():
        raise NotImplementedError()
    