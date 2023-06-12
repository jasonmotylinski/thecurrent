import data

from flask import Blueprint

api_routes = Blueprint('routes', __name__)

@api_routes.route('/api/popular/last_week/artist_title')
def get_popular_artist_title_last_week():
    return data.get_popular_artist_title_last_week().to_json()

@api_routes.route('/api/popular/last_week/artist')
def get_popular_artist_last_week():
    return data.get_popular_artist_last_week().to_json()

@api_routes.route('/api/new/last_90_days')
def get_new_last_90_days():
    return data.get_new_last_90_days().to_json()

@api_routes.route('/api/popular/all_time/artist_timeseries')
def get_popular_all_time_timeseries():
    return data.get_popular_all_time_timeseries().to_json()

@api_routes.route('/api/popular/all_time/artist')
def get_popular_all_time():
    return data.get_popular_all_time().to_json()

@api_routes.route('/api/popular/all_time/<day_of_week>/<hour>')
def get_popular_day_hour_data(day_of_week, hour):
    return data.get_popular_day_hour_data(hour, day_of_week).to_json()