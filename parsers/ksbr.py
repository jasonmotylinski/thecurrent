import bs4 as bs
from datetime import datetime, timezone, timedelta
import requests
from parsers import BaseParser


class KsbrParser(BaseParser):

    def __init__(self, config):
        super().__init__(config)

    def get_songs(self, date):
        """Get songs for the given date by fetching and parsing the KSBR playlist page."""
        # Format date as MM/DD/YYYY
        date_str = date.strftime("%m/%d/%Y")
        
        url = f"https://www.thesocalsound.org/on-the-socal-sound/playlist/?date={date_str}&host=&action_doPlayListSearch=search"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Request failed for KSBR date {date_str}: {e}")
            return
        
        soup = bs.BeautifulSoup(response.text, 'html.parser')
        
        # Find all list-item divs
        list_items = soup.find_all('div', class_='list-item row')
        
        for item in list_items:
            song_data = self._parse_song_item(item, date)
            if song_data:
                yield song_data

    def _parse_song_item(self, item, date):
        """Parse a single song item."""
        try:
            # Get artist and time
            pl_artist = item.find('div', class_='pl-artist')
            if not pl_artist:
                return None
            
            artist_span = pl_artist.find('span', class_='artist')
            artist = artist_span.text.strip() if artist_span else None
            
            time_span = pl_artist.find('span', class_='time')
            time_str = time_span.text.strip().strip('()') if time_span else None
            
            # Get song and album
            pl_song = item.find('div', class_='pl-song')
            if not pl_song:
                return None
            
            song_text = pl_song.text.strip()
            if '|' in song_text:
                song_title, album = song_text.split('|', 1)
                song_title = song_title.strip()
                album = album.strip()
            else:
                song_title = song_text
                album = None
            
            # Parse played_at
            played_at = self._parse_time(time_str, date)
            
            if artist and song_title and played_at:
                return {
                    "song": song_title,
                    "artist": artist,
                    "album": album,
                    "played_at": played_at.isoformat()
                }
        except Exception as e:
            print(f"Error parsing song item: {e}")
            return None

    def _parse_time(self, time_str, date):
        """Parse time string to datetime."""
        if not time_str:
            return None
        try:
            # Time format like "11:56 PM"
            dt = datetime.strptime(f"{date.strftime('%Y-%m-%d')} {time_str}", "%Y-%m-%d %I:%M %p")
            # KSBR is in Los Angeles, PST/PDT
            return dt.replace(tzinfo=timezone(timedelta(hours=-8)))
        except ValueError:
            return None