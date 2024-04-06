import dash
import config
import data
from pages.components import service_rows


dash.register_page(__name__, 
                   path=config.WFUV.PATH,
                   title=config.WFUV.TITLE)

layout = service_rows(config.WFUV, data)