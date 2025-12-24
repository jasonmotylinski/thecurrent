# Artist/Title Normalization for Cross-Station Queries

## Problem
Artist and title names have inconsistent capitalization across stations (e.g., "Taylor Swift" vs "taylor swift"). Cross-station queries like `hidden_gems` and `deep_cuts` fail to group these correctly because they use case-sensitive matching.

## Solution
Add `title_lower` column to the DuckDB transform (matching existing `artist_lower` pattern) and update cross-station queries to group by normalized columns.

---

## Implementation Steps

### Step 1: Add `title_lower` to Transform

**File:** `sql/transforms/songs_day_of_week_hour.sql`

Add `LOWER(title) AS title_lower` after line 6:

```sql
CREATE OR REPLACE TABLE postgres.songs_day_of_week_hour AS
SELECT
    CAST(service_id AS INT) as service_id,
    artist,
    LOWER(artist) AS artist_lower,
    title,
    LOWER(title) AS title_lower,           -- ADD THIS LINE
    CAST(played_at AS DATE) as played_at,
    ...
```

Add new index at the end of the file:
```sql
CREATE INDEX IF NOT EXISTS played_at_artist_lower_title_lower_idx
    ON postgres.songs_day_of_week_hour (played_at, artist_lower, title_lower);
```

---

### Step 2: Update `station_hidden_gems.sql`

**File:** `sql/station_hidden_gems.sql`

Replace entire file with:

```sql
SELECT artist, title,
       plays_here,
       plays_elsewhere
FROM (
    SELECT
           MAX(artist) AS artist,
           MAX(title) AS title,
           artist_lower,
           title_lower,
           SUM(CASE WHEN service_id = %(service_id)s THEN ct ELSE 0 END) as plays_here,
           SUM(CASE WHEN service_id != %(service_id)s THEN ct ELSE 0 END) as plays_elsewhere
    FROM songs_day_of_week_hour
    WHERE played_at >= CURRENT_DATE - INTERVAL '90 DAY'
      AND artist_lower != ''
      AND title_lower != ''
    GROUP BY artist_lower, title_lower
) sub
WHERE plays_here >= 3
  AND plays_elsewhere < 20
ORDER BY plays_here DESC, plays_elsewhere ASC
LIMIT 10
```

**Key changes:**
- GROUP BY `artist_lower, title_lower` instead of `artist, title`
- Use `MAX(artist)` and `MAX(title)` for display names
- Filter on `_lower` columns

---

### Step 3: Update `deep_cuts.sql`

**File:** `sql/deep_cuts.sql`

Replace entire file with:

```sql
WITH song_stats AS (
    SELECT
        MAX(artist) AS artist,
        MAX(title) AS title,
        artist_lower,
        title_lower,
        COUNT(DISTINCT service_id) as station_count,
        SUM(ct) as total_plays,
        MAX(ct) as max_station_plays
    FROM songs_day_of_week_hour
    WHERE
        played_at >= CURRENT_DATE - INTERVAL '90 DAY'
        AND artist_lower != ''
        AND title_lower != ''
    GROUP BY artist_lower, title_lower
)
SELECT
    artist,
    title,
    station_count,
    total_plays,
    ROUND(total_plays * 1.0 / station_count, 1) as avg_plays_per_station
FROM song_stats
WHERE
    station_count >= 4
    AND total_plays < 100
    AND max_station_plays < 30
ORDER BY station_count DESC, total_plays ASC
LIMIT 10;
```

---

### Step 4: Re-run Transform

After making changes, run the DuckDB transform to recreate the table:

```bash
python transform.py
```

---

## Files to Modify

| File | Change |
|------|--------|
| `sql/transforms/songs_day_of_week_hour.sql` | Add `title_lower` column + index |
| `sql/station_hidden_gems.sql` | Group by normalized columns |
| `sql/deep_cuts.sql` | Group by normalized columns |

---

## Testing

1. Verify `title_lower` column exists:
   ```sql
   SELECT title, title_lower FROM songs_day_of_week_hour LIMIT 5;
   ```

2. Test hidden gems returns results correctly grouped
3. Test deep cuts `station_count` is accurate for songs with case variations
4. Dashboard testing: verify both endpoints work
