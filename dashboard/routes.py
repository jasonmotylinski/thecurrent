import config
import data

from flask import Blueprint

api_routes = Blueprint('routes', __name__)

@api_routes.route('/api/<service_name>/popular/last_week/artist_title')
def get_popular_artist_title_last_week(service_name):
    return data.get_popular_artist_title_last_week(config.SERVICES[service_name].SERVICE_ID).to_json()

@api_routes.route('/api/<service_name>/popular/last_week/artist')
def get_popular_artist_last_week(service_name):
    return data.get_popular_artist_last_week(config.SERVICES[service_name].SERVICE_ID).to_json()

@api_routes.route('/api/<service_name>/new/last_90_days')
def get_new_last_90_days(service_name):
    return data.get_new_last_90_days(config.SERVICES[service_name].SERVICE_ID).to_json()

@api_routes.route('/api/<service_name>/popular/all_time/artist_timeseries')
def get_popular_all_time_timeseries(service_name):
    return data.get_popular_all_time_timeseries(config.SERVICES[service_name].SERVICE_ID).to_json()

@api_routes.route('/api/<service_name>/popular/all_time/artist')
def get_popular_all_time(service_name):
    return data.get_popular_all_time(config.SERVICES[service_name].SERVICE_ID).to_json()

@api_routes.route('/api/<service_name>/popular/all_time/<day_of_week>/<hour>')
def get_popular_day_hour_data(service_name, day_of_week, hour):
    return data.get_popular_day_hour_data(config.SERVICES[service_name].SERVICE_ID, hour, day_of_week).to_json()