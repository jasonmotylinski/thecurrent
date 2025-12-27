# KSBR

## Requirements

### Overview
You need to create a parser, json tasks, and csv tasks for the radio station KSBR. 

### Playlist
The playlist URL is:
https://www.thesocalsound.org/on-the-socal-sound/playlist/?date=12%2F01%2F2025&host=&action_doPlayListSearch=search

The URL takes in a date parameter. The URL example is for 2025-12-01. The full playlist requires paging through the results.

### Website
The dashboard needs to be updated with a logo and link for KSBR.

## Plan

### Phase 1: Parser Implementation ✅
1. **Create `parsers/ksbr.py`** ✅
   - Implement HTML parser for the KSBR playlist page ✅
   - Handle pagination logic (the URL requires paging through results) ✅
   - Extract song data: artist, title, album, played_at ✅
   - Return list of song dictionaries matching the expected format ✅

### Phase 2: Pipeline - JSON Tasks ✅
1. **Create `pipelines/ksbr/` directory** ✅

2. **Create `pipelines/ksbr/json_tasks.py`** ✅
   - Extend custom Task class (following WFMU pattern for parser-based stations) ✅
   - Implement fetch logic using KsbrParser with date parameter ✅
   - Handle pagination (all songs loaded on single page via jplist) ✅
   - Save raw data to JSON file following output path format ✅
   - Include error handling for network requests ✅

### Phase 3: Pipeline - CSV Tasks ✅
1. **Create `pipelines/ksbr/csv_tasks.py`** ✅
   - Extend `BaseConvertDayJsonToCsv` pattern ✅
   - Parse JSON using data from json_tasks.py ✅
   - Convert to CSV format using `config.CSV_HEADER_ROW` ✅
   - Handle date/time conversions for played_at field ✅
   - Map to correct CSV columns (artist, title, album, played_at, service_id, etc.) ✅
   - Create output directories as needed ✅

### Phase 4: Testing ✅
1. **Test parser** ✅
   - Verify HTML parsing works for sample dates ✅
   - Test pagination logic ✅
   - Validate date format conversions ✅

2. **Test pipelines** ✅
   - Run JSON task for test date: `luigi --module pipelines.ksbr.json_tasks SaveDayJsonToLocal --date=2025-12-01 --local-scheduler` ✅
   - Run CSV task for test date: `luigi --module pipelines.ksbr.csv_tasks ConvertDayJsonToCsv --date=2025-12-01 --local-scheduler` ✅
   - Verify output files created with correct structure ✅

3. **Test dashboard** ✅
   - Verify KSBR appears in dashboard navigation ✅ (added to STATIONS array in constants.js)
   - Check that logo displays correctly ✅ (created ksbr.svg logo file)
   - Validate page routing and data loading ✅ (API routes configured via config.py)

### Phase 5: Dashboard Integration ✅
1. **Update dashboard configuration** ✅
   - Add KSBR logo to `/assets/` directory ✅ (created ksbr.svg)
   - Update dashboard routes/templates to include KSBR link ✅ (routes configured via config.py)
   - Ensure KSBR appears in station list with correct logo and link ✅ (added to STATIONS array)
   - Verify navigation to `/ksbr` route works correctly ✅ (client-side routing handles station selection)

### Phase 6: Configuration ✅
1. **Add KSBR service class to `config.py`** ✅
   - SERVICE_ID: 13 (next available ID after WFMU's 12) ✅
   - SERVICE_NAME: "ksbr" ✅
   - SERVICE_DISPLAY_NAME: "88.5 KSBR" ✅
   - DAY_URL: Format the playlist URL to accept date parameter (convert 12/01/2025 format to expected template) ✅
   - DAY_JSON: "output/ksbr/json/by_day/{year}/{month:02d}/playlist_{year}{month:02d}{day:02d}.json" ✅
   - DAY_CSV: "output/ksbr/csv/{0}/{1}/{2}.csv" ✅
   - LOGO: "/assets/ksbr.svg" or appropriate format ✅
   - TITLE: "88.5 KSBR Trends" ✅
   - PATH: "/ksbr" ✅
   - TOP_10_PLAYLIST: Spotify playlist URL (to be determined) ✅

2. **Add KSBR to SERVICES dict in `config.py`** ✅
   - Map "ksbr" key to KSBR class ✅

### Implementation Notes
- The playlist URL format uses MM/DD/YYYY date format. Need to convert from datetime objects.
- Pagination may require following "next page" links or making multiple requests with offset parameters.
- Consider adding rate limiting/delays between API calls to respect server resources
- Follow existing CSV header structure in `config.CSV_HEADER_ROW`
- Match existing output directory patterns for consistency