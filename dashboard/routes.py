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

def get_station_by_id(service_id):
    """Get station info by service_id"""
    for key, service_class in config.SERVICES.items():
        if service_class.SERVICE_ID == service_id:
            return {'id': key, 'name': service_class.SERVICE_DISPLAY_NAME}
    return None

@api_routes.route('/api/<service_name>')
def get_service(service_name):
    service = config.SERVICES[service_name]
    return api_response({"title": service.TITLE, "logo": service.LOGO, "display_name": service.SERVICE_DISPLAY_NAME, "service_id": service.SERVICE_ID})

@api_routes.route('/api/<service_name>/popular/last_week/artist_title')
def get_popular_artist_title_last_week(service_name):
    try:
        df = data.get_popular_artist_title_last_week(config.SERVICES[service_name].SERVICE_ID)
        records = df.to_dict('records')
        return api_response(records)
    except Exception as e:
        return api_error(str(e), 500)

@api_routes.route('/api/<service_name>/popular/last_week/artist_title_timeseries')
def get_popular_artist_title_timeseries_route(service_name):
    """Get weekly timeseries data for top 10 popular songs in a single batch call."""
    try:
        df = data.get_popular_artist_title_timeseries(config.SERVICES[service_name].SERVICE_ID)
        records = df.to_dict('records')
        # Convert year/week to yw format for sparkline compatibility
        for record in records:
            record['yw'] = f"{record['year']}{str(record['week']).zfill(2)}"
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
    
@api_routes.route('/api/last_updated')
def last_updated():
    last_update = data.get_last_updated()
    return jsonify({
        'last_updated': last_update.isoformat()
    })

@api_routes.route('/api/search')
def search():
    query = request.args.get('q', '').strip()

    if len(query) < 2:
        return api_error('Search query must be at least 2 characters', 400)

    if len(query) > 100:
        return api_error('Search query too long', 400)

    try:
        df = data.search_songs(query)
        records = df.to_dict('records')

        return api_response(records)
    except Exception as e:
        return api_error(str(e), 500)

@api_routes.route('/api/artist/<artist>/analytics')
def get_artist_analytics_route(artist):
    try:
        analytics_df = data.get_artist_analytics(artist)
        top_songs_df = data.get_artist_top_songs(artist)
        top_songs_timeseries_df = data.get_artist_top_songs_timeseries(artist)

        analytics_records = analytics_df.to_dict('records')
        for record in analytics_records:
            station_info = get_station_by_id(record['service_id'])
            record['station_name'] = station_info['name'] if station_info else 'Unknown'
            record['station_id'] = station_info['id'] if station_info else None
            if 'month' in record and record['month'] is not None:
                month_val = record['month']
                if hasattr(month_val, 'isoformat'):
                    record['month'] = month_val.isoformat()
                elif isinstance(month_val, (int, float)):
                    record['month'] = datetime.fromtimestamp(month_val / 1000).isoformat()

        top_songs_records = top_songs_df.to_dict('records')

        top_songs_timeseries_records = top_songs_timeseries_df.to_dict('records')
        for record in top_songs_timeseries_records:
            if 'month' in record and record['month'] is not None:
                month_val = record['month']
                if hasattr(month_val, 'isoformat'):
                    record['month'] = month_val.isoformat()
                elif isinstance(month_val, (int, float)):
                    record['month'] = datetime.fromtimestamp(month_val / 1000).isoformat()

        return api_response({
            'artist': artist,
            'analytics': analytics_records,
            'top_songs': top_songs_records,
            'top_songs_timeseries': top_songs_timeseries_records
        })
    except Exception as e:
        return api_error(str(e), 500)

@api_routes.route('/api/song/analytics')
def get_song_analytics_route():
    artist = request.args.get('artist', '').strip()
    title = request.args.get('title', '').strip()

    if not artist or not title:
        return api_error('Missing required parameters: artist and title', 400)

    try:
        df = data.get_song_analytics(artist, title)
        records = df.to_dict('records')

        for record in records:
            station_info = get_station_by_id(record['service_id'])
            record['station_name'] = station_info['name'] if station_info else 'Unknown'
            record['station_id'] = station_info['id'] if station_info else None
            if 'month' in record and record['month'] is not None:
                month_val = record['month']
                if hasattr(month_val, 'isoformat'):
                    record['month'] = month_val.isoformat()
                elif isinstance(month_val, (int, float)):
                    record['month'] = datetime.fromtimestamp(month_val / 1000).isoformat()

        return api_response({
            'artist': artist,
            'title': title,
            'analytics': records
        })
    except Exception as e:
        return api_error(str(e), 500)

@api_routes.route('/api/stations')
def get_stations():
    """Get all station configurations from config.py, sorted by name"""
    stations = []
    for service_name, service_class in config.SERVICES.items():
        stations.append({
            'id': service_name,
            'name': service_class.SERVICE_DISPLAY_NAME,
            'logo': service_class.LOGO,
            'style': service_class.CSS_CLASS
        })
    # Sort stations alphabetically by name
    stations.sort(key=lambda x: x['name'])
    return api_response(stations)

@api_routes.route('/api/<service_name>/exclusives')
def get_station_exclusives_route(service_name):
    """Get artists played exclusively on this station in the last 90 days."""
    try:
        df = data.get_station_exclusives(config.SERVICES[service_name].SERVICE_ID)
        records = df.to_dict('records')
        return api_response(records)
    except Exception as e:
        return api_error(str(e), 500)

@api_routes.route('/api/<service_name>/hidden-gems')
def get_station_hidden_gems_route(service_name):
    """Get songs this station champions that aren't getting play elsewhere."""
    try:
        df = data.get_station_hidden_gems(config.SERVICES[service_name].SERVICE_ID)
        records = df.to_dict('records')
        return api_response(records)
    except Exception as e:
        return api_error(str(e), 500)

@api_routes.route('/api/deep-cuts')
def get_deep_cuts_route():
    """Get songs with low play counts but played across multiple stations."""
    try:
        df = data.get_deep_cuts()
        records = df.to_dict('records')
        return api_response(records)
    except Exception as e:
        return api_error(str(e), 500)

@api_routes.route('/api/genres/by-hour/<service_name>')
def get_genre_by_hour_route(service_name):
    """Get genre distribution by hour of day for a station."""
    try:
        service_id = config.SERVICES[service_name].SERVICE_ID
        df = data.get_genre_by_hour(service_id)
        records = df.to_dict('records')
        return api_response(records)
    except Exception as e:
        return api_error(str(e), 500)