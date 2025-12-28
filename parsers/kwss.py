import bs4 as bs
from datetime import datetime, timezone, timedelta
import requests
from parsers import BaseParser


class KwssParser(BaseParser):

    def __init__(self, config):
        super().__init__(config)

    def get_songs(self, date):
        """Get songs for the given date by fetching and parsing the KWSS playlist page."""
        # Calculate the playlist number (days from today)
        today = datetime.now().date()
        days_diff = (today - date).days
        
        if days_diff == 0:
            # Today has no number in URL
            url = "https://onlineradiobox.com/us/kwsslp/playlist/?cs=us.kwsslp"
        else:
            url = f"https://onlineradiobox.com/us/kwsslp/playlist/{days_diff}?cs=us.kwsslp"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return
        
        soup = bs.BeautifulSoup(response.text, 'html.parser')
        
        # Find the playlist table
        table = soup.find('table', class_='tablelist-schedule')
        if not table:
            return
        
        table_rows = table.find_all('tr')
        
        for row in table_rows:
            song_data = self._parse_table_row(row, date)
            if song_data:
                yield song_data

    def _parse_table_row(self, row, date):
        """Parse a single table row."""
        try:
            # Get time from span.time--schedule
            time_span = row.find('span', class_='time--schedule')
            if not time_span:
                return None

            time_str = time_span.text.strip()

            # Get song info from td.track_history_item
            track_td = row.find('td', class_='track_history_item')
            if not track_td:
                return None

            # Get text content, whether it's in an <a> tag or as plain text
            song_text = track_td.get_text(strip=True)

            # Split by " - " to get artist, title, album
            parts = song_text.split(' - ', 2)
            if len(parts) < 2:
                return None
            
            artist = parts[0].strip()
            title = parts[1].strip()
            album = parts[2].strip() if len(parts) > 2 else None
            
            # Parse played_at
            played_at = self._parse_time(time_str, date)
            
            if artist and title and played_at:
                return {
                    "song": title,
                    "artist": artist,
                    "album": album,
                    "played_at": played_at.isoformat()
                }
            return None
        except Exception as e:
            return None

    def _parse_time(self, time_str, date):
        """Parse time string to datetime."""
        if not time_str:
            return None
        try:
            # Time format is HH:MM (24-hour)
            dt = datetime.strptime(f"{date.strftime('%Y-%m-%d')} {time_str}", "%Y-%m-%d %H:%M")
            # KWSS is in Wisconsin, Central Time (CST/CDT)
            return dt.replace(tzinfo=timezone(timedelta(hours=-6)))  # Using CST (-6) for now
        except ValueError:
            return None