import dash
import config
import data
from pages.components import service_rows


dash.register_page(__name__, 
                   path=config.KUTX.PATH,
                   title=config.KUTX.TITLE)

def run():
     return service_rows(config.KUTX, data)

layout = run