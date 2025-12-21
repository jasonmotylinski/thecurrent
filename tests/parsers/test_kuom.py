import config
import io
import json
import pytest
from datetime import datetime, timezone, timedelta
from parsers.kuom import KuomParser


CDT = timezone(timedelta(hours=-5))


def make_spin_html(song, artist, time, album=""):
    """Helper to create a single spin HTML element."""
    return f'''
    <li class="spinitron_playlist__spin">
        <div class="spinitron_playlist__spin--start">{time}</div>
        <div class="spinitron_playlist__spin--info">
            <div class="spinitron_playlist__spin--song">{song}</div>
            <div class="spinitron_playlist__spin--album">{album}</div>
            <div class="spinitron_playlist__spin--artist">{artist}</div>
        </div>
    </li>
    '''


def make_playlist_json(spins_html):
    """Wrap spin HTML in the expected JSON structure."""
    data = [{"command": "insert", "method": None, "selector": None,
             "data": f'<ul class="spinitron_playlist__spins">{spins_html}</ul>'}]
    return io.StringIO(json.dumps(data))


class TestKuomParserInit:
    def test_parser_accepts_config(self):
        parser = KuomParser(config=config.KUOM)
        assert parser is not None

    def test_parser_is_base_parser_subclass(self):
        from parsers import BaseParser
        assert issubclass(KuomParser, BaseParser)


class TestGetSongsBasic:
    def test_parses_single_song(self):
        html = make_spin_html("Test Song", "Test Artist", "3:00 pm")
        reader = make_playlist_json(html)
        parser = KuomParser(config=config.KUOM)
        test_date = datetime(2025, 4, 12)

        songs = list(parser.get_songs(reader, test_date))

        assert len(songs) == 1
        assert songs[0]['song'] == 'Test Song'
        assert songs[0]['artist'] == 'Test Artist'

    def test_parses_multiple_songs(self):
        html = (make_spin_html("Song One", "Artist One", "1:00 pm") +
                make_spin_html("Song Two", "Artist Two", "1:05 pm") +
                make_spin_html("Song Three", "Artist Three", "1:10 pm"))
        reader = make_playlist_json(html)
        parser = KuomParser(config=config.KUOM)
        test_date = datetime(2025, 4, 12)

        songs = list(parser.get_songs(reader, test_date))

        assert len(songs) == 3

    def test_all_songs_have_required_fields(self):
        html = (make_spin_html("Song A", "Artist A", "2:00 pm") +
                make_spin_html("Song B", "Artist B", "2:05 pm"))
        reader = make_playlist_json(html)
        parser = KuomParser(config=config.KUOM)
        test_date = datetime(2025, 4, 12)

        songs = list(parser.get_songs(reader, test_date))

        for song in songs:
            assert 'song' in song
            assert 'artist' in song
            assert 'played_at' in song


class TestTimeParsing:
    def test_parses_am_time(self):
        html = make_spin_html("Morning Song", "Artist", "9:30 am")
        reader = make_playlist_json(html)
        parser = KuomParser(config=config.KUOM)
        test_date = datetime(2025, 4, 12)

        songs = list(parser.get_songs(reader, test_date))

        assert songs[0]['played_at'].hour == 9
        assert songs[0]['played_at'].minute == 30

    def test_parses_pm_time(self):
        html = make_spin_html("Afternoon Song", "Artist", "3:45 pm")
        reader = make_playlist_json(html)
        parser = KuomParser(config=config.KUOM)
        test_date = datetime(2025, 4, 12)

        songs = list(parser.get_songs(reader, test_date))

        assert songs[0]['played_at'].hour == 15
        assert songs[0]['played_at'].minute == 45

    def test_parses_noon(self):
        html = make_spin_html("Noon Song", "Artist", "12:00 pm")
        reader = make_playlist_json(html)
        parser = KuomParser(config=config.KUOM)
        test_date = datetime(2025, 4, 12)

        songs = list(parser.get_songs(reader, test_date))

        assert songs[0]['played_at'].hour == 12

    def test_parses_midnight(self):
        html = make_spin_html("Midnight Song", "Artist", "12:05 am")
        reader = make_playlist_json(html)
        parser = KuomParser(config=config.KUOM)
        test_date = datetime(2025, 4, 12)

        songs = list(parser.get_songs(reader, test_date))

        assert songs[0]['played_at'].hour == 0
        assert songs[0]['played_at'].minute == 5

    def test_includes_cdt_timezone(self):
        html = make_spin_html("Song", "Artist", "5:00 pm")
        reader = make_playlist_json(html)
        parser = KuomParser(config=config.KUOM)
        test_date = datetime(2025, 4, 12)

        songs = list(parser.get_songs(reader, test_date))

        assert songs[0]['played_at'].tzinfo == CDT

    def test_date_matches_input_date(self):
        html = make_spin_html("Song", "Artist", "5:00 pm")
        reader = make_playlist_json(html)
        parser = KuomParser(config=config.KUOM)
        test_date = datetime(2025, 6, 15)

        songs = list(parser.get_songs(reader, test_date))

        assert songs[0]['played_at'].year == 2025
        assert songs[0]['played_at'].month == 6
        assert songs[0]['played_at'].day == 15


class TestHtmlEntityHandling:
    def test_decodes_apostrophe_entity(self):
        html = make_spin_html("She&#039;s Electric", "Oasis", "12:55 am")
        reader = make_playlist_json(html)
        parser = KuomParser(config=config.KUOM)
        test_date = datetime(2025, 4, 12)

        songs = list(parser.get_songs(reader, test_date))

        assert songs[0]['song'] == "She's Electric"

    def test_decodes_ampersand_entity(self):
        html = make_spin_html("Tom &amp; Jerry", "Artist", "1:00 pm")
        reader = make_playlist_json(html)
        parser = KuomParser(config=config.KUOM)
        test_date = datetime(2025, 4, 12)

        songs = list(parser.get_songs(reader, test_date))

        assert songs[0]['song'] == "Tom & Jerry"

    def test_strips_whitespace(self):
        html = '''
        <li class="spinitron_playlist__spin">
            <div class="spinitron_playlist__spin--start">  3:00 pm  </div>
            <div class="spinitron_playlist__spin--info">
                <div class="spinitron_playlist__spin--song">
                    Spacey Song
                </div>
                <div class="spinitron_playlist__spin--artist">
                    Whitespace Artist
                </div>
            </div>
        </li>
        '''
        reader = make_playlist_json(html)
        parser = KuomParser(config=config.KUOM)
        test_date = datetime(2025, 4, 12)

        songs = list(parser.get_songs(reader, test_date))

        assert songs[0]['song'] == "Spacey Song"
        assert songs[0]['artist'] == "Whitespace Artist"


class TestWithRealData:
    def test_parses_real_playlist_file(self):
        with open('tests/data/kuom/playlist_20250412.json', 'r') as f:
            parser = KuomParser(config=config.KUOM)
            test_date = datetime(2025, 4, 12)

            songs = list(parser.get_songs(f, test_date))

            assert len(songs) > 0

    def test_real_data_first_song_values(self):
        with open('tests/data/kuom/playlist_20250412.json', 'r') as f:
            parser = KuomParser(config=config.KUOM)
            test_date = datetime(2025, 4, 12)

            songs = list(parser.get_songs(f, test_date))
            first_song = songs[0]

            assert first_song['song'] == "She's Electric"
            assert first_song['artist'] == "Oasis"
            assert first_song['played_at'].hour == 0
            assert first_song['played_at'].minute == 55

    def test_real_data_all_dates_match(self):
        with open('tests/data/kuom/playlist_20250412.json', 'r') as f:
            parser = KuomParser(config=config.KUOM)
            test_date = datetime(2025, 4, 12)

            songs = list(parser.get_songs(f, test_date))

            for song in songs:
                assert song['played_at'].date() == test_date.date()

    def test_real_data_all_have_timezone(self):
        with open('tests/data/kuom/playlist_20250412.json', 'r') as f:
            parser = KuomParser(config=config.KUOM)
            test_date = datetime(2025, 4, 12)

            songs = list(parser.get_songs(f, test_date))

            for song in songs:
                assert song['played_at'].tzinfo == CDT
