import config
import json
import logging
from dashboard import data
from rawkit_playlist import playlist

def update_popular_artist_title_last_week_playlist(service_id, service_name):
    artist_titles = json.loads(data.get_popular_artist_title_last_week(service_id=service_id).to_json(orient='table'))['data']
    playlist_data=[{"artist_name": at['artist'], "song_name": at['title']} for at in artist_titles]
    playlist.update_playlist("Rawk-it - {0} - Weekly Top 10".format(service_name.upper()), "", playlist_data)


if __name__=="__main__": 
    logging.basicConfig(level=logging.INFO)
    update_popular_artist_title_last_week_playlist(config.THECURRENT.SERVICE_ID, config.THECURRENT.SERVICE_NAME)
    update_popular_artist_title_last_week_playlist(config.KEXP.SERVICE_ID, config.KEXP.SERVICE_NAME)
    update_popular_artist_title_last_week_playlist(config.KUTX.SERVICE_ID, config.KUTX.SERVICE_NAME)
    update_popular_artist_title_last_week_playlist(config.WXPN.SERVICE_ID, config.WXPN.SERVICE_NAME)
    update_popular_artist_title_last_week_playlist(config.WFUV.SERVICE_ID, config.WFUV.SERVICE_NAME)
    update_popular_artist_title_last_week_playlist(config.KCRW.SERVICE_ID, config.KCRW.SERVICE_NAME)
    update_popular_artist_title_last_week_playlist(config.KUOM.SERVICE_ID, config.KUOM.SERVICE_NAME)
