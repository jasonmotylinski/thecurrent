from rapidfuzz import process, fuzz
import csv
import os
from db import get_engine


def execute_query(query):
    """Execute a SQL query and return the first column as a list."""
    with get_engine().connect() as conn:
        import pandas as pd
        df = pd.read_sql(query, conn)
        return df.iloc[:, 0].tolist()


def get_choices():
    return execute_query("SELECT DISTINCT artist FROM songs_day_of_week_hour WHERE service_id = 1 ORDER BY artist")


def get_comparison_artists():
    return execute_query("SELECT DISTINCT artist FROM songs_day_of_week_hour WHERE service_id != 1 ORDER BY artist")


def load_existing_artists(csv_path):
    """Load existing artist names from CSV file."""
    existing = set()
    if os.path.exists(csv_path):
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(row["artist"])
    return existing


def normalize_and_write(csv_path, choices, comparison_artists):
    """Find matching artists and write results to CSV."""
    existing_artists = load_existing_artists(csv_path)
    file_is_new = not existing_artists

    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)

        if file_is_new:
            writer.writerow(["artist", "artist_normalized"])
            f.flush()

        for artist in comparison_artists:
            if artist in existing_artists:
                continue

            match = process.extractOne(artist, choices, scorer=fuzz.WRatio)
            if 91 <= match[1] < 100:
                writer.writerow([artist, match[0]])
                f.flush()


def main():
    """Main entry point."""
    choices = get_choices()
    comparison_artists = get_comparison_artists()
    csv_path = "data/artist_normalized.csv"

    normalize_and_write(csv_path, choices, comparison_artists)


if __name__ == "__main__":
    main()