import dash
import config
import data
from pages.components import service_rows


dash.register_page(__name__, 
                   path=config.KCRW.PATH,
                   title=config.KCRW.TITLE)

layout = service_rows(config.KCRW, data)