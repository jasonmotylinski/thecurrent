from rapidfuzz import process, fuzz
import csv
import os
from db import get_engine


def execute_query(query):
    """Execute a SQL query and return the first column as a list."""
    with get_engine().connect() as conn:
        import pandas as pd
        df = pd.read_sql(query, conn)
        return df.to_dict('records')


def get_choices():
    print("Loading choice titles...")
    return execute_query("SELECT DISTINCT artist, title FROM songs_day_of_week_hour WHERE service_id = 1 AND artist != '' AND title!='' ORDER BY artist, title")

def get_comparison_titles():
    print("Loading comparison titles...")
    return execute_query("SELECT DISTINCT artist, title FROM songs_day_of_week_hour WHERE service_id != 1 AND artist != '' AND title!='' ORDER BY artist, title")

def create_choice_mapping(choices):
    """Create a dict mapping 'artist title' strings to their dict records."""
    return {f"{record['artist']} {record['title']}": record for record in choices}


def load_existing_titles(csv_path):
    """Load existing title names from CSV file."""
    existing = set()
    if os.path.exists(csv_path):
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(row["title"])
    return existing


def normalize_and_write(csv_path, choice_mapping, comparison_titles):
    """Find matching titles and write results to CSV."""
    existing_titles = load_existing_titles(csv_path)
    file_is_new = not existing_titles
    choice_keys = list(choice_mapping.keys())

    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)

        if file_is_new:
            writer.writerow(["title", "title_normalized"])
            f.flush()

        for record in comparison_titles:
            print(f"Processing record: {record}")
            if record['title'] in existing_titles:
                continue

            query = f"{record['artist']} {record['title']}"
            match = process.extractOne(query, choice_keys, scorer=fuzz.WRatio)
            if 92 <= match[1] < 100:
                matched_record = choice_mapping[match[0]]
                print(f"Matched: {record} to {matched_record}")
                writer.writerow([record['title'], matched_record['title']])
                f.flush()


def main():
    """Main entry point."""
    choices = get_choices()
    choice_mapping = create_choice_mapping(choices)
    comparison_titles = get_comparison_titles()
    csv_path = "data/title_normalized.csv"

    normalize_and_write(csv_path, choice_mapping, comparison_titles)


if __name__ == "__main__":
    main()