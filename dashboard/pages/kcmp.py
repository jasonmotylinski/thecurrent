import dash
import config
import data
from pages.components import service_rows


dash.register_page(__name__, 
                   path=config.THECURRENT.PATH,
                   title=config.THECURRENT.TITLE)

layout = service_rows(config.THECURRENT, data)