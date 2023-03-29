import data
import dash_bootstrap_components as dbc
import flask
import plotly.express as px

from dash import Dash, dash_table, html, dcc, Input, Output
from datetime import datetime, timedelta


def popular_artist_title_last_week_cell():
    df=data.get_popular_artist_title_last_week()
    end_date=datetime.utcnow()
    start_date=end_date - timedelta(90)

    rows=[
        html.Tr([
            html.Th("Artist"),
            html.Th("Title")
        ])
    ]
    
    for d in df.to_dict('records'):
        df_timeseries=data.get_title_timeseries(d['artist'], d['title'],start_date, end_date)
        fig = px.line(df_timeseries, x="ymw", y="ct", height=20, width=200)
        fig.update_xaxes(visible=False, fixedrange=True)
        fig.update_yaxes(visible=False, fixedrange=True)
        fig.update_layout(annotations=[], overwrite=True)
        fig.update_layout(
            showlegend=False,
            plot_bgcolor="white",
            margin=dict(l=0, r=0, t=0, b=0)
        )

        rows.append(html.Tr([
            html.Td(d['artist']),
            html.Td(d['title']),
            html.Td(children=[dcc.Graph(figure=fig, config={'displayModeBar': False})])
        ]))


    
    return dbc.Col([
                html.H3("Top 10 Most Popular Songs in the Last Week", className="text-center"),
                html.Table(rows, className="table")
            ], md=6)

def popular_artist_last_week_cell():
    df=data.get_popular_artist_last_week()
    df=df.rename(columns={"ct":"total plays"})
    df['title - artist']="<b>" + df['title'] + '</b> <br> ' + df['artist']
    fig = px.treemap(df,
                    path=[px.Constant("all"),'artist', 'title'],
                    values='total plays',
                    color='total plays',
                    color_continuous_scale='RdBu',
                    maxdepth=2
                    )
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    fig.update_traces(hovertemplate='%{label}<br> Total Plays: %{value}')
    fig.update_traces(root_color="lightgrey")
    fig.update_coloraxes(showscale=False)
    return dbc.Col([
                html.H3("Top 10 Most Popular Artists in the Last Week", className="text-center"),
                dcc.Graph(figure=fig, id='popular_artist_last_week_graph', config={'displayModeBar': False})

            ], md=6)

def get_hourly_count_by_day_of_week(df, day_of_week):
    return df[df['day_of_week']==day_of_week]['ct'].to_list()

def new_last_90_days_cell():
    df=data.get_new_last_90_days()
    sunday=get_hourly_count_by_day_of_week(df, "Sunday")
    monday=get_hourly_count_by_day_of_week(df, "Monday")
    tuesday=get_hourly_count_by_day_of_week(df, "Tuesday")
    wednesday=get_hourly_count_by_day_of_week(df, "Wednesday")
    thursday=get_hourly_count_by_day_of_week(df, "Thursday")
    friday=get_hourly_count_by_day_of_week(df, "Friday")
    saturday=get_hourly_count_by_day_of_week(df, "Saturday")

    day_counts=[sunday, monday, tuesday, wednesday, thursday, friday, saturday]
    fig = px.imshow(day_counts,
                labels=dict(x="hour", y="day", color="count of plays"),
                x=['00','01','02','03','04','05','06','07','08','09','10','11','12',
                   '13','14','15','16','17','18','19','20','21','22','23'],
                y=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],
                color_continuous_scale='deep'
            )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_coloraxes(showscale=False)

    return dbc.Col([
                html.H3("Time of Week New Music is Played", className="text-center"),
                dcc.Graph(figure=fig, id='new_last_90_days', config={'displayModeBar': False},style={'height': '200px'})
            ], md=6)

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
    ],
    md=6)

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
                popular_artist_title_last_week_cell(),
                popular_artist_last_week_cell(),
                
            ]),
            dbc.Row([
                new_last_90_days_cell(),
                popular_day_hour()
            ]),
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

