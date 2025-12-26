import bs4 as bs
from datetime import datetime, timezone, timedelta
import requests
import re
from parsers import BaseParser


class WfmuParser(BaseParser):

    def __init__(self, config):
        super().__init__(config)

    def _generate_time_slots(self, date):
        """Generate all time slots for the given date (every 3 minutes)."""
        year, month, day = date.year, date.month, date.day
        for hour_12 in range(1, 13):  # 1 to 12
            for meridian in ['am', 'pm']:  # AM/PM
                for minute in range(0, 60, 3):  # 00, 03, ..., 57
                    yield {
                        'hour_12': hour_12,
                        'meridian': meridian,
                        'minute': minute,
                        'year': year,
                        'month': month,
                        'day': day
                    }

    def _convert_to_24_hour(self, hour_12, meridian):
        """Convert 12-hour format to 24-hour."""
        if meridian == 'am':  # AM
            return 0 if hour_12 == 12 else hour_12
        else:  # PM
            return 12 if hour_12 == 12 else hour_12 + 12

    def _parse_played_time(self, time_str, date):
        """Parse the played time string and return datetime object."""
        if not time_str:
            return None
        # Assume format like "6:00 AM" or "6:00AM"
        time_str = time_str.strip()
        # Use regex to extract hour, minute, meridian
        match = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM|am|pm|a|p)?', time_str)
        if match:
            hour_12 = int(match.group(1))
            minute = int(match.group(2))
            meridian = match.group(3).lower() if match.group(3) else 'am'  # default to AM if not specified
            
            hour_24 = self._convert_to_24_hour(hour_12, meridian[0])  # 'a' or 'p'
            
            played_at = datetime(date.year, date.month, date.day, hour_24, minute)
            played_at = played_at.replace(tzinfo=timezone(timedelta(hours=-5)))
            return played_at
        return None

    def _query_timesearch(self, time_slot):
        """Query timesearch.php for the given time slot and return parsed songs."""
        url = 'https://www.wfmu.org/timesearch.php'
        data = {
            'month': str(time_slot['month']),
            'day': str(time_slot['day']),
            'year': str(time_slot['year']),
            'hour_12': str(time_slot['hour_12']),
            'minute': f'{time_slot["minute"]:02d}',
            'meridian': time_slot['meridian'],
            'submit': 'Find the song or show!'
        }
     
        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()  # Raise for bad status codes
        except requests.exceptions.RequestException as e:
            print(f"Request failed for time slot {time_slot}: {e}")
            return []  # Return empty list on error
        
        soup = bs.BeautifulSoup(response.text, 'html.parser')
        
        songs = []
        tables = soup.find_all('table')
       
        for table in tables:
            
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 5:
                    artist = cols[2].text.strip()
                    song_raw = cols[3].text.strip()
                    if artist and song_raw:
                        # Extract song title
                        match = re.search(r'"([^"]+)"', song_raw)
                        song = match.group(1) if match else song_raw.split('\n')[0].strip()
                        
                        # Album if present
                        album = cols[4].text.strip() if len(cols) > 2 and cols[4].text.strip() else None
                        
                        # Time if present (assume it's in cols[3])
                        played_time_str = cols[0].text.strip() if len(cols) > 3 and cols[0].text.strip() else None
                        
                        songs.append({
                            'artist': artist,
                            'song': song,
                            'album': album,
                            'played_time_str': played_time_str
                        })
        return songs

    def get_songs(self, date):
        """Get songs for the given date by querying timesearch.php for each time slot."""
        seen_songs = set()  # Track unique songs to avoid duplicates
        
        for time_slot in self._generate_time_slots(date):
            songs = self._query_timesearch(time_slot)
            for song in songs:
                # Create a unique key for deduplication
                song_key = (song['artist'], song['song'], song['album'], song['played_time_str'])
                if song_key in seen_songs:
                    continue  # Skip duplicate
                seen_songs.add(song_key)
                
                # Use played_time from the table if available, otherwise fallback to time_slot
                played_at = self._parse_played_time(song['played_time_str'], date)
                if not played_at:
                    # Fallback to constructed time
                    hour_24 = self._convert_to_24_hour(time_slot['hour_12'], time_slot['meridian'])
                    played_at = datetime(
                        time_slot['year'], time_slot['month'], time_slot['day'],
                        hour_24, time_slot['minute']
                    ).replace(tzinfo=timezone(timedelta(hours=-5)))
                
                yield {
                    "song": song['song'],
                    "artist": song['artist'],
                    "played_at": played_at.isoformat(),
                    "album": song['album']
                }
            