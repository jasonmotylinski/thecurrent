import config
import dashboard.data as data
import json
from datetime import datetime

from flask import Blueprint, request, Response

api_routes = Blueprint('routes', __name__)

@api_routes.route('/api/<service_name>')
def get_service(service_name):
    service = config.SERVICES[service_name]
    return Response(
        json.dumps({"title": service.TITLE, "logo": service.LOGO}),
        mimetype='application/json'
    )

@api_routes.route('/api/<service_name>/popular/last_week/artist_title')
def get_popular_artist_title_last_week(service_name):
    df = data.get_popular_artist_title_last_week(config.SERVICES[service_name].SERVICE_ID)
    # Convert DataFrame to list of dictionaries
    records = df.to_dict('records')
    return Response(
        json.dumps(records),
        mimetype='application/json'
    )

@api_routes.route('/api/<service_name>/popular/last_week/artist')
def get_popular_artist_last_week(service_name):
    df = data.get_popular_artist_last_week(config.SERVICES[service_name].SERVICE_ID)
    records = df.to_dict('records')
    return Response(
        json.dumps(records),
        mimetype='application/json'
    )

@api_routes.route('/api/<service_name>/new/last_90_days')
def get_new_last_90_days(service_name):
    df = data.get_new_last_90_days(config.SERVICES[service_name].SERVICE_ID)
    records = df.to_dict('records')
    return Response(
        json.dumps(records),
        mimetype='application/json'
    )

@api_routes.route('/api/<service_name>/popular/all_time/artist_timeseries')
def get_popular_all_time_timeseries(service_name):
    df = data.get_popular_all_time_timeseries(config.SERVICES[service_name].SERVICE_ID)
    records = df.to_dict('records')
    return Response(
        json.dumps(records),
        mimetype='application/json'
    )

@api_routes.route('/api/<service_name>/popular/all_time/artist')
def get_popular_all_time(service_name):
    df = data.get_popular_all_time(config.SERVICES[service_name].SERVICE_ID)
    records = df.to_dict('records')
    return Response(
        json.dumps(records),
        mimetype='application/json'
    )

@api_routes.route('/api/<service_name>/popular/all_time/<day_of_week>/<hour>')
def get_popular_day_hour_data(service_name, day_of_week, hour):
    df = data.get_popular_day_hour_data(config.SERVICES[service_name].SERVICE_ID, hour, day_of_week)
    records = df.to_dict('records')
    return Response(
        json.dumps(records),
        mimetype='application/json'
    )

@api_routes.route('/api/<service_name>/title_timeseries')
def get_title_timeseries(service_name):
    artist = request.args.get('artist')
    title = request.args.get('title')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if not all([artist, title, start_date_str, end_date_str]):
        return Response(
            json.dumps({'error': 'Missing required parameters'}),
            status=400,
            mimetype='application/json'
        )
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return Response(
            json.dumps({'error': 'Invalid date format. Use YYYY-MM-DD'}),
            status=400,
            mimetype='application/json'
        )
    
    df = data.get_title_timeseries(
        artist=artist,
        title=title,
        start_date=start_date,
        end_date=end_date,
        service_id=config.SERVICES[service_name].SERVICE_ID
    )
    # Convert DataFrame to list of dictionaries
    records = df.to_dict('records')
    return Response(
        json.dumps(records),
        mimetype='application/json'
    )