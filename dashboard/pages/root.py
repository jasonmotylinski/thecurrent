import dash
import config
import data
from pages.components import service_rows


dash.register_page(__name__, 
                   path='',
                   title=config.THECURRENT.TITLE)

def run():
     return service_rows(config.THECURRENT, data)

layout = run