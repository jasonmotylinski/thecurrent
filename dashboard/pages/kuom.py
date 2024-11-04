import dash
import config
import data
from pages.components import service_rows


dash.register_page(__name__, 
                   path=config.KUOM.PATH,
                   title=config.KUOM.TITLE)

def run():
     return service_rows(config.KUOM, data)

layout = run