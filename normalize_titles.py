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
    return execute_query("SELECT DISTINCT title FROM songs_day_of_week_hour WHERE service_id = 1 ORDER BY title")


def get_comparison_titles():
    return execute_query("SELECT DISTINCT title FROM songs_day_of_week_hour WHERE service_id != 1 ORDER BY title")


def load_existing_titles(csv_path):
    """Load existing title names from CSV file."""
    existing = set()
    if os.path.exists(csv_path):
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(row["title"])
    return existing


def normalize_and_write(csv_path, choices, comparison_titles):
    """Find matching titles and write results to CSV."""
    existing_titles = load_existing_titles(csv_path)
    file_is_new = not existing_titles

    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)

        if file_is_new:
            writer.writerow(["title", "title_normalized"])
            f.flush()

        for title in comparison_titles:
            print(f"Processing title: {title}")
            if title in existing_titles:
                continue

            match = process.extractOne(title, choices, scorer=fuzz.WRatio)
            if 91 <= match[1] < 100:
                writer.writerow([title, match[0]])
                f.flush()


def main():
    """Main entry point."""
    choices = get_choices()
    comparison_titles = get_comparison_titles()
    csv_path = "data/title_normalized.csv"

    normalize_and_write(csv_path, choices, comparison_titles)


if __name__ == "__main__":
    main()