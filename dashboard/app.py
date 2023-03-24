# app.py

import config
import dash_bootstrap_components as dbc
import flask
import pandas as pd
import plotly.express as px
import sqlite3

from dash import Dash, dash_table, html, dcc, Input, Output
from datetime import datetime, timedelta
from dateutil import parser

def get_yesterday():
    return datetime.utcnow() - timedelta(days=1)

def get_last_week_range():
    end_date=datetime.utcnow() - timedelta(days=1)
    start_date=datetime.utcnow() - timedelta(days=7)
    return {"start_date": start_date, "end_date": end_date}

def popular_last_week_cell():
    last_week=get_last_week_range()
    end_date=last_week["end_date"]
    start_date=last_week["start_date"]
    t="""
    SELECT artist, title, COUNT(*) as ct
    FROM songs
    WHERE played_at >= '{start_date.year}-{start_date.month:02d}-{start_date.day:02d}T00:00:00.000-06:00'
    AND played_at <= '{end_date.year}-{end_date.month:02d}-{end_date.day:02d}T23:59:59.000-06:00'
    GROUP BY artist, title
    ORDER BY ct DESC
    LIMIT 10
    """.format(start_date=start_date, end_date=end_date)

    con = sqlite3.connect(config.DB)
    df = pd.read_sql(t, con)
    return dbc.Col([
                html.H3("Top 10 Most Popular Songs in the Last Week", className="text-center"),
                dash_table.DataTable(df.to_dict('records'), 
                                        [{"name": i, "id": i} for i in df.columns],
                                        style_cell={'font-family':'sans-serif','textAlign': 'left'},
                                        style_header={'fontWeight': 'bold', 'background_color': '#ffffff', 'border_top': '0px'},
                                        style_as_list_view=True)
            ], md=4)

def new_yesterday_cell():
    yesterday=get_yesterday()
    t="""
    SELECT 
        a.artist, 
        a.title, 
        a.played_at
    FROM songs a
    INNER JOIN (
        SELECT 
            artist, 
            title, 
            played_at, 
            DENSE_RANK() OVER (
            PARTITION BY artist, title
            ORDER BY played_at ASC) AS rank
        FROM songs
        WHERE trim(artist) != ''
        or trim(title) != ''
    ) b
    ON a.artist=b.artist
    AND a.title=b.title
    AND a.played_at=b.played_at
    WHERE  b.rank=1
    AND b.played_at >= '{yesterday.year}-{yesterday.month:02d}-{yesterday.day:02d}T00:00:00.000-06:00'
    AND b.played_at <= '{yesterday.year}-{yesterday.month:02d}-{yesterday.day:02d}T23:59:59.000-06:00'
    ORDER BY a.played_at DESC
    LIMIT 100
    """.format(yesterday=yesterday)

    con = sqlite3.connect(config.DB)
    df = pd.read_sql(t, con)
    return dbc.Col([
                html.H3("Songs played for the first time yesterday", className="text-center"),
                dash_table.DataTable(df.to_dict('records'), 
                                     [{"name": i, "id": i} for i in df.columns],
                                     style_cell={'font-family':'sans-serif','textAlign': 'left'},
                                     style_header={'fontWeight': 'bold', 'background_color': '#ffffff', 'border_top': '0px'},
                                     style_as_list_view=True)
            ], md=5)


def popular_all_time_graph():
    t = """
    SELECT 
        artist, 
        year,
        month,
        year || "-" || month AS year_month, 
        COUNT(*) as ct 
    FROM songs 
    WHERE artist IN(
        SELECT artist
        FROM songs 
        GROUP BY artist
        ORDER BY COUNT(*) DESC
        LIMIT 5
    )
    GROUP BY artist, year, month
    ORDER BY year, month ASC
    """
    con = sqlite3.connect(config.DB)
    df_timeseries = pd.read_sql(t, con)
    fig=px.line(df_timeseries, x="year_month", y="ct", color="artist" )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return dbc.Col([dcc.Graph(figure=fig, id='popular_graph', config={'displayModeBar': False})])


def get_popular_all_time_data(start_date=None, end_date=None):
    where=""

    if start_date and end_date:
        where="WHERE played_at >='{0}' AND played_at <='{1}'".format(start_date, end_date)
    t = """SELECT artist, COUNT(*) as ct 
        FROM songs
        {where}
        GROUP BY artist
        ORDER BY ct DESC
        LIMIT 5""".format(where=where)
    con = sqlite3.connect(config.DB)
    return pd.read_sql(t, con)


def popular_all_time():
    df=get_popular_all_time_data()
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
    


def get_popular_day_hour_data(hour, day_of_week):
    
    
    t="""SELECT 
    artist, 
    COUNT(*) as ct
    FROM songs
    WHERE day_of_week='{day_of_week}'
    AND hour={hour}
    AND artist != ''
    GROUP BY artist
    ORDER BY ct DESC
    LIMIT 5""".format(hour=hour, day_of_week=day_of_week)
    con = sqlite3.connect(config.DB)
    return pd.read_sql(t, con)


def popular_day_hour():
   
    hour=datetime.utcnow().hour
    day_of_week=datetime.utcnow().strftime("%A")
    hour_label=datetime.now().strftime("%-I %p")

    df_now=get_popular_day_hour_data( hour, day_of_week)
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
    return get_popular_day_hour_data(hour, day_of_week).to_dict('records')

@app.callback(Output('popular_day_hour_title', 'children'),
              Input('interval', 'n_intervals'))
def handle_interval_callback_2(n):
    day_of_week=datetime.utcnow().strftime("%A")
    hour_label=datetime.now().strftime("%-I %p")
    return "Top 5 Most Popular Artists Played on {day_of_week} at {hour_label}".format(day_of_week=day_of_week, hour_label=hour_label)

if __name__ == '__main__':
    app.run_server(debug=False)

