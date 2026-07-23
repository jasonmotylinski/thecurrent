# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**The Current** is a Python data pipeline that aggregates playlist data from 11 independent radio stations (89.3 The Current, KEXP, KUTX, WXPN, WFUV, KCRW, KUOM, KKXT, WEHM, WNXP, WYEP), stores it in PostgreSQL, and serves analytics through a Flask dashboard.

## Common Commands

```bash
# Environment setup
virtualenv venv && source venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=.

# Running Luigi pipelines (from project root)
luigi --module pipelines.kexp.json_tasks SaveDayJsonToLocal --date=2024-01-01 --local-scheduler
luigi --module pipelines.kexp.csv_tasks ConvertDayJsonToCsv --date=2024-01-01 --local-scheduler
luigi --module pipelines.kexp.json_tasks SaveMonthJsonToLocal --year=2024 --month=1 --local-scheduler

# For The Current (HTML-based scraping)
luigi --module pipelines.thecurrent.html_tasks SaveDayHtmlToLocal --date=2024-01-01 --local-scheduler
luigi --module pipelines.thecurrent.csv_tasks ConvertDayHtmlToCsv --date=2024-01-01 --local-scheduler

# Dashboard
python dashboard/server.py

# Tests
pytest
```

## Architecture

```
Radio Station APIs → Luigi Pipelines → PostgreSQL → Flask API → Redis Cache
    (JSON/HTML)      (ETL to CSV)       (songs)     (routes.py)  (caching)
```

### Key Layers

1. **Pipeline Layer** (`pipelines/`): Luigi-based ETL tasks
   - Base classes in `pipelines/__init__.py`: `BaseSaveDayJsonToLocal`, `BaseConvertDayJsonToCsv`
   - Each station has its own subdirectory with `json_tasks.py` and `csv_tasks.py`
   - Pattern: Fetch JSON → Parse to CSV → Insert to database

2. **Configuration** (`config.py`): Service definitions with API URLs, file paths, service IDs
   - Each service is a class (e.g., `KEXP`, `KUTX`) with constants
   - `SERVICES` dict maps service names to their config classes

3. **Dashboard** (`dashboard/`): Flask web app
   - `routes.py`: REST endpoints
   - `data.py`: Database queries with Redis caching
   - SQL queries stored in `sql/` directory

4. **Metadata Enrichment**: Separate pipelines for MusicBrainz, Spotify, Wikipedia, Discogs, Every Noise

### Database

- Primary: PostgreSQL (connection in `config.DB_PG_CONN`)
- Cache: Redis (5-min to daily expiration)
- Main table: `songs` (artist, title, played_at, service_id, 30+ fields)
- See `datamodel.md` for full ER diagram

## Adding a New Radio Station

1. Add service class to `config.py` with API URL, paths, service ID
2. Create `pipelines/[service_name]/` directory
3. Implement `json_tasks.py` extending `BaseSaveDayJsonToLocal`
4. Implement `csv_tasks.py` extending `BaseConvertDayJsonToCsv`
5. Add to `SERVICES` dict in config.py

## Linting

Ruff is configured in `pyproject.toml` (ignores E501 long lines).

## Production: server01

The live Spotify playlist is updated on **server01** by cron (`crontab -l` under user `jason`):

```
*/2 * * * * /home/jason/code/thecurrent/scripts/server01/run_playlists_live.sh  >> /var/log/thecurrent/thecurrent_run_playlists_live.log 2>&1
5 1  * * *  .../run_daily_pipeline.sh  >> /var/log/thecurrent/thecurrent_daily_pipeline.log 2>&1
45 1 * * *  .../run_transforms.sh      >> /var/log/thecurrent/transforms.log 2>&1
5 2  * * *  .../run_playlists.sh        >> /var/log/thecurrent/playlists.log 2>&1
```

`run_playlists_live.sh` activates the venv and runs `playlist_kcmp_last100played.py`
(scrapes thecurrent.org → updates Spotify playlist `3PolUEn6bpV7PPQO8EKkAc`). Code lives at
`/home/jason/code/thecurrent` (a git checkout — check `git log` there for the deployed commit).

### Troubleshooting "playlist stopped updating"

Diagnose on the box, don't guess from the code. SSH in and check the log + token, not just recent commits.

1. **Log:** `tail -60 /var/log/thecurrent/thecurrent_run_playlists_live.log`
   - The script configures logging *after* `from rawkit_playlist import playlist` (line 8), and that
     import calls `spotify.current_user()` at module load. So an auth failure crashes **before** any
     JSON log line is written — the last JSON timestamp in the log marks when it last worked.

2. **Most common cause — Spotify OAuth token can't refresh.** spotipy falls back to the interactive
   flow ("Enter the URL you were redirected to:") and cron has no TTY, so it dies with
   `EOFError: EOF when reading a line`. Inspect the token cache:
   ```
   cd /home/jason/code/thecurrent
   python3 -c "import json; d=json.load(open('.cache')); print(sorted(d)); print('refresh:', bool(d.get('refresh_token')))"
   ```
   If `refresh_token` is **False/missing**, that's the bug — access tokens last ~1h and can't self-renew.
   **Fix:** re-auth once interactively so a refresh token is written, then cron self-heals:
   ```
   cd /home/jason/code/thecurrent && source venv/bin/activate && python playlist_kcmp_last100played.py
   ```
   Paste the redirect URL when prompted, then re-run the key check to confirm `refresh_token` is present.

3. **Log bloat:** every-2-min crashes append full tracebacks and the log can grow to ~GB. Truncate with
   `truncate -s 0 /var/log/thecurrent/thecurrent_run_playlists_live.log` (no logrotate configured).

Note: the `America/New_York` vs `America/Chicago` timezone in `get_recent_songs()` has churned across
commits (`8464ce7` even introduced `'America/New York'` with a space — an invalid pytz name). Verify
the deployed commit, but it's rarely the cause of a full outage — auth is.
