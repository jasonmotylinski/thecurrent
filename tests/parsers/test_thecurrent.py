import pytest
from datetime import datetime
from pipelines.thecurrent.playlist import get_songs


class TestGetSongsWithRealData:
    def test_parses_real_playlist_file(self):
        with open('tests/data/thecurrent/playlist_20251220.html', 'r') as f:
            html = f.read()
            songs = list(get_songs(html))
            assert len(songs) > 0

    def test_all_songs_have_required_fields(self):
        with open('tests/data/thecurrent/playlist_20251220.html', 'r') as f:
            html = f.read()
            songs = list(get_songs(html))

            for song in songs:
                assert 'title' in song
                assert 'artist' in song
                assert 'album' in song
                assert 'played_at' in song
                assert 'id' in song

    def test_played_at_is_datetime(self):
        with open('tests/data/thecurrent/playlist_20251220.html', 'r') as f:
            html = f.read()
            songs = list(get_songs(html))

            for song in songs:
                assert isinstance(song['played_at'], datetime)

    def test_first_song_has_expected_date(self):
        with open('tests/data/thecurrent/playlist_20251220.html', 'r') as f:
            html = f.read()
            songs = list(get_songs(html))
            first_song = songs[0]

            assert first_song['played_at'].year == 2025
            assert first_song['played_at'].month == 12
            assert first_song['played_at'].day == 20


class TestGetSongsDec21:
    def test_parses_dec21_playlist_file(self):
        with open('tests/data/thecurrent/playlist_20251221.html', 'r') as f:
            html = f.read()
            songs = list(get_songs(html))
            assert len(songs) > 0
