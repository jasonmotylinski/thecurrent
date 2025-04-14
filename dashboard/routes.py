import config
import dashboard.data as data
import json
from datetime import datetime

from flask import Blueprint, request, jsonify

api_routes = Blueprint('routes', __name__)

def api_response(data, status=200):
    """Helper function to create consistent API responses"""
    return jsonify(data), status

def api_error(message, status=400):
    """Helper function to create consistent error responses"""
    return jsonify({'error': message}), status

@api_routes.route('/api/<service_name>')
def get_service(service_name):
    service = config.SERVICES[service_name]
    return api_response({"title": service.TITLE, "logo": service.LOGO})

@api_routes.route('/api/<service_name>/popular/last_week/artist_title')
def get_popular_artist_title_last_week(service_name):
    try:
        df = data.get_popular_artist_title_last_week(config.SERVICES[service_name].SERVICE_ID)
        records = df.to_dict('records')
        return api_response(records)
    except Exception as e:
        return api_error(str(e), 500)

@api_routes.route('/api/<service_name>/popular/last_week/artist')
def get_popular_artist_last_week(service_name):
    try:
        df = data.get_popular_artist_last_week(config.SERVICES[service_name].SERVICE_ID)
        records = df.to_dict('records')
        return api_response(records)
    except Exception as e:
        return api_error(str(e), 500)

@api_routes.route('/api/<service_name>/new/last_90_days')
def get_new_last_90_days(service_name):
    try:
        df = data.get_new_last_90_days(config.SERVICES[service_name].SERVICE_ID)
        records = df.to_dict('records')
        return api_response(records)
    except Exception as e:
        return api_error(str(e), 500)

@api_routes.route('/api/<service_name>/popular/all_time/artist_timeseries')
def get_popular_all_time_timeseries(service_name):
    try:
        df = data.get_popular_all_time_timeseries(config.SERVICES[service_name].SERVICE_ID)
        records = df.to_dict('records')
        return api_response(records)
    except Exception as e:
        return api_error(str(e), 500)

@api_routes.route('/api/<service_name>/popular/all_time/artist')
def get_popular_all_time(service_name):
    try:
        df = data.get_popular_all_time(config.SERVICES[service_name].SERVICE_ID)
        records = df.to_dict('records')
        return api_response(records)
    except Exception as e:
        return api_error(str(e), 500)

@api_routes.route('/api/<service_name>/popular/all_time/<day_of_week>/<hour>')
def get_popular_day_hour_data(service_name, day_of_week, hour):
    try:
        df = data.get_popular_day_hour_data(config.SERVICES[service_name].SERVICE_ID, hour, day_of_week)
        records = df.to_dict('records')
        return api_response(records)
    except Exception as e:
        return api_error(str(e), 500)

@api_routes.route('/api/<service_name>/title_timeseries')
def get_title_timeseries(service_name):
    artist = request.args.get('artist')
    title = request.args.get('title')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if not all([artist, title, start_date_str, end_date_str]):
        return api_error('Missing required parameters')
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return api_error('Invalid date format. Use YYYY-MM-DD')
    
    try:
        df = data.get_title_timeseries(
            artist=artist,
            title=title,
            start_date=start_date,
            end_date=end_date,
            service_id=config.SERVICES[service_name].SERVICE_ID
        )
        records = df.to_dict('records')
        return api_response(records)
    except Exception as e:
        return api_error(str(e), 500)