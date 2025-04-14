import config
import json
from datetime import datetime, timezone, timedelta
from parsers.kuom import KuomParser
import pytest

def test_kuom_parser():
    # Load test data
    with open('tests/data/kuom/playlist_20250412.json', 'r') as f:
        # Create parser instance
        parser = KuomParser(config=config.KUOM)  # config is not used in the parser
        
        # Test date
        test_date = datetime(2025, 4, 12)
        
        # Get songs from parser
        songs = list(parser.get_songs(f, test_date))
        print(songs)
        # Verify the first song
        assert len(songs) > 0
        first_song = songs[0]
        
        # Check song structure
        assert 'song' in first_song
        assert 'artist' in first_song
        assert 'played_at' in first_song
        
        # Verify played_at is a datetime with correct timezone
        assert isinstance(first_song['played_at'], datetime)
        assert first_song['played_at'].tzinfo == timezone(timedelta(hours=-5))
        
        # Verify all songs have required fields
        for song in songs:
            assert all(key in song for key in ['song', 'artist', 'played_at'])
            assert isinstance(song['played_at'], datetime)
            assert song['played_at'].tzinfo == timezone(timedelta(hours=-5))
            
        # Verify date parsing
        for song in songs:
            assert song['played_at'].date() == test_date.date() 