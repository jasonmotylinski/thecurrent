import config
import data
import dash
import dash_bootstrap_components as dbc
import flask
import logging

from pages.components import sidebar
from dash import Dash, html
from flask_caching import Cache
from flask.logging import default_handler
from routes import api_routes

external_scripts =[
    "https://www.googletagmanager.com/gtag/js?id=G-HB05PVK153",
    "assets/gtag.js"
]

server = flask.Flask(__name__)
app = Dash(__name__, 
           use_pages=True,
           external_scripts=external_scripts, 
           external_stylesheets=[dbc.themes.BOOTSTRAP], 
           server=server)
app.title = "Loading..."
app.scripts.config.serve_locally = False

cache = Cache(app.server, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': config.REDIS_URL
})

server.register_blueprint(api_routes)

def serve_layout():
    return html.Div(
        [
            sidebar(config),
            
            dbc.Container(
            [
                dash.page_container,
                dbc.Row([
                    html.Div(["Developed by ", 
                            html.A("Jason Motylinski", href='https://jason.motylinski.com'), 
                            ],
                            className="text-center")
                ]),
                dbc.Row([
                    html.Div(["Data last updated:" + data.get_last_updated()], 
                            className='text-center')]),
                dbc.Row([
                    html.Div([
                                html.A("Data available on HuggingFace", href='https://huggingface.co/datasets/jasonmotylinski/89.3TheCurrentPlaylists'), 
                            ],
                            className="text-center")
                ])
            ]
             , style={
                "padding-left": "60px"
             }   
            )
        ]
    )



app.layout=serve_layout

if __name__ == '__main__':
    if config.DEBUG:
        log=logging.getLogger(config.LOGGER_NAME)
        log.setLevel(logging.DEBUG)
        log.addHandler(default_handler)
        log.info("app: Setting log level to DEBUG")
    app.run_server(debug=config.DEBUG)

