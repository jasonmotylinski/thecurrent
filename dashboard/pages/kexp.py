import dash
import config
import data
from pages.components import service_rows


dash.register_page(__name__, 
                   path=config.KEXP.PATH,
                   title=config.KEXP.TITLE)

def run():
     return service_rows(config.KEXP, data)

layout = run