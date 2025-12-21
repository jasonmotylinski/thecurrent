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
