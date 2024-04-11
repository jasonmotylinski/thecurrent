import dash
import config
import data
from pages.components import service_rows


dash.register_page(__name__, 
                   path=config.WXPN.PATH,
                   title=config.WXPN.TITLE)

def run():
     return service_rows(config.WXPN, data)

layout = run