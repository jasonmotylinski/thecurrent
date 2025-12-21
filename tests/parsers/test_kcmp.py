import pytest
from unittest.mock import patch, Mock
from parsers.kcmp import create_id, get_shows, get_schedule_html


class TestCreateId:
    def test_create_id_returns_sha256_hash(self):
        show = {
            "show_id": "show-001",
            "host_name": "Mary Lucia",
            "show_name": "The Morning Show",
            "start_time": "2025-01-01T06:00:00",
            "end_time": "2025-01-01T09:00:00"
        }
        result = create_id(show)
        assert len(result) == 64  # SHA256 hex digest length
        assert result.isalnum()

    def test_create_id_is_deterministic(self):
        show = {
            "show_id": "show-001",
            "host_name": "Mary Lucia",
            "show_name": "The Morning Show",
            "start_time": "2025-01-01T06:00:00",
            "end_time": "2025-01-01T09:00:00"
        }
        assert create_id(show) == create_id(show)

    def test_create_id_differs_for_different_shows(self):
        show1 = {
            "show_id": "show-001",
            "host_name": "Mary Lucia",
            "show_name": "The Morning Show",
            "start_time": "2025-01-01T06:00:00",
            "end_time": "2025-01-01T09:00:00"
        }
        show2 = {
            "show_id": "show-002",
            "host_name": "Jade",
            "show_name": "The Current",
            "start_time": "2025-01-01T09:00:00",
            "end_time": "2025-01-01T12:00:00"
        }
        assert create_id(show1) != create_id(show2)


class TestGetShows:
    def test_get_shows_parses_html(self):
        with open('tests/data/kcmp/schedule_20250101.html', 'r') as f:
            html = f.read()

        shows = list(get_shows(html))

        assert len(shows) == 3

    def test_get_shows_extracts_fields(self):
        with open('tests/data/kcmp/schedule_20250101.html', 'r') as f:
            html = f.read()

        shows = list(get_shows(html))
        first_show = shows[0]

        assert first_show['show_id'] == 'show-001'
        assert first_show['host_name'] == 'Mary Lucia'
        assert first_show['show_name'] == 'The Morning Show'
        assert first_show['start_time'] == '2025-01-01T06:00:00'
        assert first_show['end_time'] == '2025-01-01T09:00:00'
        assert 'id' in first_show

    def test_get_shows_generates_unique_ids(self):
        with open('tests/data/kcmp/schedule_20250101.html', 'r') as f:
            html = f.read()

        shows = list(get_shows(html))
        ids = [s['id'] for s in shows]

        assert len(ids) == len(set(ids))  # All IDs are unique

    def test_get_shows_all_have_required_fields(self):
        with open('tests/data/kcmp/schedule_20250101.html', 'r') as f:
            html = f.read()

        shows = list(get_shows(html))
        required_fields = ['id', 'show_id', 'host_name', 'show_name', 'start_time', 'end_time']

        for show in shows:
            for field in required_fields:
                assert field in show, f"Missing field: {field}"


class TestGetScheduleHtml:
    @patch('parsers.kcmp.requests.get')
    def test_get_schedule_html_makes_request(self, mock_get):
        mock_response = Mock()
        mock_response.text = '<html></html>'
        mock_get.return_value = mock_response

        from datetime import date
        test_date = date(2025, 1, 1)
        result = get_schedule_html(test_date)

        assert mock_get.called
        assert result == '<html></html>'
