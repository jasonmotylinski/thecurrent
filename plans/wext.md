# WEXT

## Requirements

### Overview
You need to create a parser, json tasks, and csv tasks for the radio station WEXT.  You need to update the website with a logo for WEXT

### Playlist
The playlist URL is:
https://api.composer.nprstations.org/v1/widget/5182cfc4e1c891fe553a5b52/now?format=json&style=v2&show_song=true . The API is similar to the existing parser and patterns for KUTX and WYEP.

The webpage contains links for the last week. it's unclear how the links on the website retrieve the day's playlist. The website currently has links for Sunday 12/21 thru Saturday 12/27.

### Website
The dashboard needs to be updated with a logo and link for WEXT. The WEXT website is at: https://www.wextradio.org/

### Scripts
Update the run scripts to include WEXT.

## Plan

### 1. Configuration (`config.py`)

Add a new `WEXT` class to config.py (after `WYEP`). Use SERVICE_ID=15 (next available after WYEP=14).

```python
class WEXT(object):
    DAY_URL="https://api.composer.nprstations.org/v1/widget/5182cfc4e1c891fe553a5b52/day?date={date.year}-{date.month:02d}-{date.day:02d}&format=json"
    DAY_JSON="output/wext/json/by_day/{year}/{month:02d}/playlist_{year}{month:02d}{day:02d}.json"
    DAY_CSV="output/wext/csv/{0}/{1}/{2}.csv"
    SERVICE_ID=15
    SERVICE_NAME="wext"
    SERVICE_DISPLAY_NAME="90.1 WEXT"
    LOGO="/assets/logos/wext.svg"
    CSS_CLASS="button-style"
    TITLE=SERVICE_DISPLAY_NAME + " Trends"
    PATH="/" + SERVICE_NAME
    TOP_10_PLAYLIST="[SPOTIFY_PLAYLIST_URL_IF_AVAILABLE]"
```

Also update the `SERVICES` dict (around line 254) to include:
```python
"wext": WEXT,
```

Determine the next available SERVICE_ID by checking the existing ids (KUTX=3, WYEP=14, etc.) and assign accordingly.

### 2. Create JSON Tasks (`pipelines/wext/json_tasks.py`)

Create a new directory `pipelines/wext/` and add `json_tasks.py`:

```python
import config
import requests
from pipelines import BaseSaveDayJsonToLocal

class SaveDayJsonToLocal(BaseSaveDayJsonToLocal):
    def __init__(self, *args, **kwargs):
        super(SaveDayJsonToLocal, self).__init__(*args, **kwargs)
        self.config = config.WEXT

    def get_json(self):
        r = requests.get(self.config.DAY_URL.format(date=self.date))
        return r.json()
```

This will fetch the NPR Composer API JSON and save it to the configured DAY_JSON path.

### 3. Create CSV Tasks (`pipelines/wext/csv_tasks.py`)

Create `pipelines/wext/csv_tasks.py` with the NPR API parser:

```python
import config
import json
import luigi
from datetime import datetime
from pipelines import create_id, BaseConvertDayJsonToCsv
from pipelines.wext.json_tasks import SaveDayJsonToLocal

class ConvertDayJsonToCsv(BaseConvertDayJsonToCsv):
    """Parse songs from the JSON for the given day."""
    date = luigi.DateParameter()

    def __init__(self, *args, **kwargs):
        super(ConvertDayJsonToCsv, self).__init__(*args, **kwargs)
        self.config = config.WEXT

    def requires(self):
        """Requires."""
        yield SaveDayJsonToLocal(self.date)

    def get_rows(self, input):
        """Parse NPR Composer API JSON format (same as KUTX/WYEP)."""
        for p in json.load(input)["onToday"]:
            records = p['playlist']
            if records:
                for s in records:
                    # WEXT uses Central Time timezone (-06:00)
                    played_at = datetime.strptime(s["_start_time"]+"-06:00", "%m-%d-%Y %H:%M:%S%z")
                    album = None
                    if 'collectionName' in s:
                        album = s["collectionName"]
                    yield [
                        create_id(played_at, s["artistName"], s["trackName"], config.WEXT.SERVICE_ID),
                        s["artistName"],
                        s["trackName"],
                        album,
                        played_at.isoformat(),
                        s["_duration"],  # Duration
                        config.WEXT.SERVICE_ID,  # Service ID
                        '',  # Empty fields 8-30 (song_id through hour)
                        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                        played_at.strftime("%Y"),
                        played_at.strftime("%m"),
                        played_at.strftime("%d"),
                        played_at.strftime("%A"),
                        played_at.strftime("%U"),
                        played_at.strftime("%H")
                    ]
```

Note: The NPR API uses the same JSON structure as KUTX and WYEP, so the parsing logic is identical. If WEXT's JSON differs, adjust the `get_rows()` method accordingly.

### 4. Update Dashboard (`dashboard/routes.py`, `dashboard/data.py`, HTML templates)

- Add WEXT to the service routing in `routes.py`
- Add WEXT query methods in `data.py` (following the KUTX/WYEP pattern)
- Update HTML templates to display WEXT in the dashboard UI with logo and link to wextradio.org

### 5. Add Logo Asset

- Place WEXT logo at `static/assets/logos/wext.svg` (or appropriate format)
- Logo should match the style of existing station logos

### 6. Update Run Scripts

- Update any shell scripts that run Luigi pipelines to include WEXT commands
- Example commands to add:
  ```bash
  luigi --module pipelines.wext.json_tasks SaveDayJsonToLocal --date=2024-01-01 --local-scheduler
  luigi --module pipelines.wext.csv_tasks ConvertDayJsonToCsv --date=2024-01-01 --local-scheduler
  ```

### Implementation Order

1. Add `WEXT` class to `config.py` and register in `SERVICES` dict
2. Create `pipelines/wext/json_tasks.py` and test with: `luigi --module pipelines.wext.json_tasks SaveDayJsonToLocal --date=2024-01-01 --local-scheduler`
3. Create `pipelines/wext/csv_tasks.py` and test with: `luigi --module pipelines.wext.csv_tasks ConvertDayJsonToCsv --date=2024-01-01 --local-scheduler`
4. Add logo asset to `static/assets/logos/wext.svg`
5. Update dashboard routes and templates to include WEXT
6. Update run scripts
7. Run full pipeline to verify integration