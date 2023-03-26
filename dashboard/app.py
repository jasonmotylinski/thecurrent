import data
import dash_bootstrap_components as dbc
import flask
import plotly.express as px

from dash import Dash, dash_table, html, dcc, Input, Output
from datetime import datetime


def popular_last_week_cell():
    df=data.get_popular_last_week()
    return dbc.Col([
                html.H3("Top 10 Most Popular Songs in the Last Week", className="text-center"),
                dash_table.DataTable(df.to_dict('records'), 
                                        [{"name": i, "id": i} for i in df.columns],
                                        style_cell={'font-family':'sans-serif','textAlign': 'left'},
                                        style_header={'fontWeight': 'bold', 'background_color': '#ffffff', 'border_top': '0px'},
                                        style_as_list_view=True)
            ], md=4)

def new_yesterday_cell():
    df=data.get_new_yesterday()
    return dbc.Col([
                html.H3("Songs played for the first time yesterday", className="text-center"),
                dash_table.DataTable(df.to_dict('records'), 
                                     [{"name": i, "id": i} for i in df.columns],
                                     style_cell={'font-family':'sans-serif','textAlign': 'left'},
                                     style_header={'fontWeight': 'bold', 'background_color': '#ffffff', 'border_top': '0px'},
                                     style_as_list_view=True)
            ], md=5)

def popular_all_time_graph():
    df=data.get_popular_all_time_timeseries()
    fig=px.line(df, x="year_month", y="ct", color="artist" )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return dbc.Col([dcc.Graph(figure=fig, id='popular_graph', config={'displayModeBar': False})])


def popular_all_time():
    df=data.get_popular_all_time()
    return dbc.Row(
        [
            dbc.Row(html.H3("Top 5 Most Popular Artists of All-Time", className="text-center", id='popular_title')),
            dbc.Row([
                dbc.Col([
            
                    dash_table.DataTable(df.to_dict('records'), 
                                         [{"name": i, "id": i} for i in df.columns],
                                         style_cell={'font-family':'sans-serif', 'textAlign': 'left'}, 
                                         style_header={'fontWeight': 'bold', 'background_color': '#ffffff', 'border_top': '0px'},
                                         style_as_list_view=True,
                                         id="popular_table")
                ]),
                popular_all_time_graph()
            ])
        ])

def popular_day_hour():
   
    hour=datetime.utcnow().hour
    day_of_week=datetime.utcnow().strftime("%A")
    hour_label=datetime.now().strftime("%-I %p")

    df_now=data.get_popular_day_hour_data( hour, day_of_week)
    return dbc.Col([
        html.H3("Top 5 Most Popular Artists Played on {day_of_week} at {hour_label}".format(day_of_week=day_of_week, hour_label=hour_label), className="text-center", id="popular_day_hour_title"),
        dash_table.DataTable(df_now.to_dict('records'), 
                             [{"name": i, "id": i} for i in df_now.columns],
                             style_cell={'font-family':'sans-serif', 'textAlign': 'left'}, 
                             style_header={'fontWeight': 'bold', 'background_color': '#ffffff', 'border_top': '0px'},
                             style_as_list_view=True,
                             id="popular_day_hour_table")
    ])

def serve_layout():
    return html.Div(
        dbc.Container(
        [
            dbc.Row(
                dbc.Col([
                    html.H1("89.3 The Current Trends", className="display-3 text-center"),
                ])
            ),
            dbc.Row([
                popular_last_week_cell(),
                new_yesterday_cell(),
            ]),
            popular_day_hour(),
            popular_all_time(),
            dcc.Interval(
                id='interval',
                interval=1*100000,
                n_intervals=0
            )
        ]
        )
    )

server = flask.Flask(__name__)
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)
app.title = "89.3 The Current Trends"
app.scripts.config.serve_locally = False
app.scripts.append_script({"external_url": "https://www.googletagmanager.com/gtag/js?id=G-HB05PVK153"})
app.scripts.append_script({"external_url": "assets/gtag.js"})

app.layout=serve_layout

@app.callback(Output('popular_day_hour_table', 'data'),
              Input('interval', 'n_intervals'))
def handle_interval_callback(n):
    hour=datetime.utcnow().hour
    day_of_week=datetime.utcnow().strftime("%A")
    return data.get_popular_day_hour_data(hour, day_of_week).to_dict('records')

@app.callback(Output('popular_day_hour_title', 'children'),
              Input('interval', 'n_intervals'))
def handle_interval_callback_2(n):
    day_of_week=datetime.utcnow().strftime("%A")
    hour_label=datetime.now().strftime("%-I %p")
    return "Top 5 Most Popular Artists Played on {day_of_week} at {hour_label}".format(day_of_week=day_of_week, hour_label=hour_label)

if __name__ == '__main__':
    app.run_server(debug=False)

