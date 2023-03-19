# app.py

import dash_bootstrap_components as dbc
import flask
import pandas as pd
import plotly.express as px
import sqlite3

from dash import Dash, dash_table, html, dcc
from datetime import datetime

con = sqlite3.connect('thecurrent.sqlite3')

t = """SELECT artist, COUNT(*) as ct 
       FROM songs 
       GROUP BY artist
       ORDER BY ct DESC
       LIMIT 5"""

df = pd.read_sql(t, con)

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
df_timeseries = pd.read_sql(t, con)
fig=px.line(df_timeseries, x="year_month", y="ct", color="artist" )


hour=datetime.utcnow().hour
hour_label=datetime.now().strftime("%-I %p")
day_of_week=datetime.utcnow().strftime("%A")
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
df_now=pd.read_sql(t, con)

def serve_layout():
    return html.Div(
       dbc.Container(
       [
              dbc.Row(
                            dbc.Col([
                                   html.H1("89.3 The Current Trends", className="display-3 text-center"),
                                     html.H3("Top 5 Most Popular Artists of All-Time", className="text-center"),
                            ])
                     ),
              dbc.Row(
                     [
                            dbc.Col([
                                   dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns],style_cell={'font-family':'sans-serif'})
                            ]),
                            dbc.Col([dcc.Graph(figure=fig)])
                     ]),
              dbc.Row(
                     dbc.Col([
                            html.H3("Top 5 Most Popular Artists Played on {day_of_week} at {hour_label}".format(day_of_week=day_of_week, hour_label=hour_label), className="text-center"),
                            dash_table.DataTable(df_now.to_dict('records'), [{"name": i, "id": i} for i in df.columns],style_cell={'font-family':'sans-serif'})
                     ])
              )
       ]
       ))

server = flask.Flask(__name__)
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)
app.title = "89.3 The Current Trends"
app.scripts.config.serve_locally = False
app.scripts.append_script({"external_url": "https://www.googletagmanager.com/gtag/js?id=G-HB05PVK153"})


app.layout=serve_layout

if __name__ == '__main__':
    app.run_server(debug=False)

