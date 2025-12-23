# New Analytics Implementation Plan

## Completed: File Decomposition ✅

Refactored frontend code into modular files:

### JavaScript (load in order):
- `dashboard/assets/constants.js` - API config, stations, color schemes (48 lines)
- `dashboard/assets/utils.js` - Date formatting, API fetch helpers (28 lines)
- `dashboard/assets/charts.js` - Plotly chart functions (352 lines)
- `dashboard/assets/script.js` - Vue app only (449 lines, down from 843)

### HTML Templates (Jinja2 includes):
- `dashboard/templates/index.html` - Main template
- `dashboard/templates/partials/loading.html` - Loading overlay
- `dashboard/templates/partials/sidebar.html` - Station navigation
- `dashboard/templates/partials/search.html` - Search input & results
- `dashboard/templates/partials/analytics.html` - Artist/song analytics view
- `dashboard/templates/partials/dashboard.html` - Main dashboard content
- `dashboard/templates/partials/footer.html` - Footer links

### Key Changes:
- Vue uses `${...}` delimiters to avoid Jinja2 conflicts
- Flask uses `render_template()` instead of `send_from_directory()`
- Old `dashboard/index.html` can be deleted

---

## Completed: Phase 1 (Quick Wins) ✅

### 1. Station Exclusives ✅
- **SQL**: `sql/station_exclusives.sql` - Artists played only on one station in last 90 days
- **Data**: `data.get_station_exclusives(service_id)` with daily cache
- **API**: `GET /api/<service_name>/exclusives`
- **Frontend**: Table with numbered rankings (gray text), clickable artists
- **Optimization**: Rewrote query with window function to avoid 82M row nested loop join (54s → <1s)
- **Status**: COMPLETE

### 2. Deep Cuts Finder ✅
- **SQL**: `sql/deep_cuts.sql` - Songs played on 4+ stations but <100 total plays
- **Data**: `data.get_deep_cuts()` with daily cache
- **API**: `GET /api/deep-cuts`
- **Frontend**: Table with station count badges (gray), artist links
- **Status**: COMPLETE

### 3. Time-of-Day Genre Patterns ✅
- **SQL**: `sql/genre_by_hour.sql` - Genre distribution by hour from Spotify metadata
- **Data**: `data.get_genre_by_hour()` with daily cache
- **API**: `GET /api/genres/by-hour`
- **Frontend**: Plotly heatmap (15 genres × 24 hours)
- **Status**: COMPLETE

---

## Remaining: Phase 2 (Discovery Features)

### 4. Rising Artists Detection
**What**: Algorithmic detection using 30/60/90 day velocity metrics and momentum scores
**Value**: Discover breakout artists before they hit mainstream
**Complexity**: Medium

**Implementation Steps:**
1. Create `sql/rising_artists.sql`:
   - Calculate plays for last 30, 30-60, 60-90 day periods
   - Compute growth rates: `(plays_30d - plays_30_60d) / plays_30_60d * 100`
   - Calculate momentum score: average of 30d and 60d growth
   - Filter: `growth_30d_pct > 50` and `plays_30d >= 10`
   - Return: artist, plays_30d, station_count, growth_30d_pct, momentum_score
   - Order by momentum_score DESC, limit 20

2. Add to `dashboard/data.py`:
   ```python
   def get_rising_artists(service_id=None):
       """Get artists with rising momentum in last 90 days."""
       filename = 'rising_artists.sql'
       params = {"service_id": service_id} if service_id else {}
       return get_data(filename, in_5_minutes(), params)  # 5-min cache
   ```

3. Add to `dashboard/routes.py`:
   ```python
   @api_routes.route('/api/rising-artists')
   def get_rising_artists_route():
       try:
           service_id = request.args.get('service_id', type=int)
           df = data.get_rising_artists(service_id)
           return api_response(df.to_dict('records'))
       except Exception as e:
           return api_error(str(e), 500)
   ```

4. Frontend (`dashboard/assets/script.js`):
   - Add reactive state: `const risingArtists = ref([])`
   - Create function: `loadRisingArtists(stationId = null)`
   - Fetch from `/api/rising-artists?service_id={id}`
   - Display as card list with:
     - Artist name (clickable)
     - Momentum percentage badge
     - Station count badge
     - Mini sparkline (optional)

5. Frontend (`dashboard/index.html`):
   - Add new section "Rising Artists"
   - Card-based layout with artist images (if available)
   - Show momentum indicator (up arrow + percentage)
   - Filter toggle: "All Stations" vs current station

---

### 5. Genre Diversity Dashboard
**What**: Shannon entropy analysis of genre distribution per station
**Value**: Understand which stations are most/least eclectic
**Complexity**: Medium

**Implementation Steps:**
1. Create `sql/station_genre_diversity.sql`:
   - Join songs_day_of_week_hour with artist_genres (source='spotify')
   - Calculate genre proportions per station
   - Compute Shannon entropy: `-SUM(proportion * LN(proportion))`
   - Count unique genres per station
   - Aggregate top genres as JSON array
   - Return: service_id, unique_genres, diversity_score, top_genres

2. Add to `dashboard/data.py`:
   ```python
   def get_genre_diversity():
       """Get genre diversity metrics by station."""
       filename = 'station_genre_diversity.sql'
       return get_data(filename, tomorrow_at_105_am_est())
   ```

3. Add to `dashboard/routes.py`:
   ```python
   @api_routes.route('/api/stations/genre-diversity')
   def get_genre_diversity_route():
       try:
           df = data.get_genre_diversity()
           return api_response(df.to_dict('records'))
       except Exception as e:
           return api_error(str(e), 500)
   ```

4. Frontend:
   - Horizontal bar chart: diversity scores by station
   - Side-by-side donut charts: top genres per station
   - Sortable table showing all metrics

---

### 6. Station Similarity Matrix
**What**: Heatmap showing which stations have similar tastes based on top 100 artist overlap
**Value**: "If you like KEXP, try KUTX" recommendations
**Complexity**: Medium

**Implementation Steps:**
1. Create `sql/station_similarity.sql`:
   - CTE to get top 100 artists per station (last 90 days)
   - Self-join stations on shared artists
   - Count shared artists between each pair
   - Calculate similarity percentage: `shared_artists / 100 * 100`
   - Return: station1_id, station2_id, shared_artists, similarity_pct

2. Add to `dashboard/data.py`:
   ```python
   def get_station_similarity():
       """Get station similarity matrix based on artist overlap."""
       filename = 'station_similarity.sql'
       return get_data(filename, tomorrow_at_105_am_est())
   ```

3. Add to `dashboard/routes.py`:
   ```python
   @api_routes.route('/api/stations/similarity')
   def get_station_similarity_route():
       try:
           df = data.get_station_similarity()
           return api_response(df.to_dict('records'))
       except Exception as e:
           return api_error(str(e), 500)
   ```

4. Frontend:
   - Plotly heatmap: 11×11 symmetric matrix
   - Color scale: light (low similarity) to dark (high similarity)
   - Hover: show shared artist count + percentage
   - Click: modal with list of shared artists

---

## Remaining: Phase 3 (Advanced Analytics)

### 7. Collaborative Filtering Recommendations
**What**: "If you like artist X, you'll love artist Y" based on co-listening patterns
**Complexity**: Complex (requires optimization)

**Key Implementation Notes:**
- Use artist co-occurrence across stations
- Calculate affinity score: `co_occurrence_stations * SQRT(plays_a * plays_b)`
- May need database index: `CREATE INDEX idx_service_artist ON songs_day_of_week_hour(service_id, artist)`
- Add to artist analytics page as "Similar Artists" section

### 8. Artist Lifecycle Analysis
**What**: Categorize artists as Emerging/Rising Star/Established/Classic/Fading
**Complexity**: Complex (requires songs_metadata join)

**Key Implementation Notes:**
- Join with songs_metadata for first_release_date
- Calculate years_active: `AGE(CURRENT_DATE, first_release_date)`
- Define lifecycle stages based on age + growth trends
- Display as segmented tabs with filterable artist lists

---

## Remaining: Phase 4 (Future Enhancements)

### 9. Weekly Discovery Playlist Generator
**What**: Auto-generated 20-song playlist combining rising artists, deep cuts, and exclusives
**Implementation**: Combine results from analytics #2, #4, #5 with randomization

### 10. Year-over-Year Station Trends
**What**: Compare current year's top artists/genres to previous year
**Implementation**: Requires full year of historical data, temporal comparison query

---

## Database Optimization Completed ✅

### Indexes added to `songs_day_of_week_hour`:
```sql
-- Existing indexes
CREATE INDEX service_title_played_at_idx ON songs_day_of_week_hour (service_id, artist, title, played_at);
CREATE INDEX service_artist_title_idx ON songs_day_of_week_hour (service_id, artist, title);

-- New indexes for date-range queries
CREATE INDEX played_at_service_artist_idx ON songs_day_of_week_hour (played_at, service_id, artist);
CREATE INDEX played_at_artist_service_idx ON songs_day_of_week_hour (played_at, artist, service_id);
CREATE INDEX played_at_artist_lower_service_idx ON songs_day_of_week_hour (played_at, artist_lower, service_id);
```

### Column added:
- `artist_lower` - Lowercase artist name for case-insensitive matching without runtime `LOWER()` calls

### Query optimization pattern:
- Use CTEs with window functions instead of self-joins
- Example: `COUNT(*) OVER (PARTITION BY artist_lower)` to count stations per artist in single pass
- Avoid nested loops that cause O(n²) comparisons

---

## Database Optimization Considerations (Future)

For Phase 3 complex queries, consider:

1. **Additional indexes if needed:**
   ```sql
   CREATE INDEX idx_artist_played_at ON songs_day_of_week_hour(artist, played_at);
   CREATE INDEX idx_service_artist ON songs_day_of_week_hour(service_id, artist);
   ```

2. **Materialized Views:**
   - Pre-aggregate artist pair affinity scores for collaborative filtering
   - Refresh daily via cron job

3. **Caching Strategy:**
   - Complex queries: 6-12 hour cache TTL
   - Simple queries: Daily cache (current pattern)
   - Dynamic queries: 5-minute cache

---

## Testing Checklist

Before deploying each phase:

- [ ] Test SQL queries directly in psql
- [ ] Verify API endpoints return valid JSON
- [ ] Test with no data / empty results
- [ ] Check Redis caching is working
- [ ] Test across all 11 stations
- [ ] Verify frontend renders correctly
- [ ] Check mobile responsiveness
- [ ] Test analytics navigation (back button)
- [ ] Verify performance (<2s load time)

---

## Performance Monitoring

Watch for:
- SQL queries taking >1 second
- API endpoints timing out
- Redis cache misses (should be <10%)
- Frontend Plotly render time
- Memory usage on large result sets
