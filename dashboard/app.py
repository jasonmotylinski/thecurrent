# app.py

import pandas as pd
import sqlite3

from dash import Dash, dash_table, html

con = sqlite3.connect('thecurrent.sqlite3')

t = """SELECT artist, COUNT(*) as ct 
       FROM songs 
       GROUP BY artist
       ORDER BY ct DESC
       LIMIT 5"""

df = pd.read_sql(t, con)

app = Dash(__name__)

table = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])
h3 = html.H3("Top 5 All-Time Artists")
app.layout = html.Div([h3, table])

if __name__ == '__main__':
    app.run_server(debug=True)

