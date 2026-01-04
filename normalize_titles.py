from rapidfuzz import process, fuzz, utils
import csv
import os
from tqdm import tqdm
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


def partition_by_first_letter(records):
    """Partition records by first letter of artist name."""
    partitions = {}
    for record in records:
        first_char = record['artist'][0].upper() if record['artist'] else '#'
        if first_char.isalpha():
            key = first_char
        elif first_char.isdigit():
            key = '0-9'
        else:
            key = 'OTHER'

        if key not in partitions:
            partitions[key] = []
        partitions[key].append(record)
    return partitions

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


def process_partition(letter, choice_partition, comparison_partition, choice_mapping, existing_titles):
    """Process a single partition of titles and return matches."""
    matches = []
    choice_keys = [f"{r['artist']} {r['title']}" for r in choice_partition]

    if not choice_keys:
        return matches

    pbar = tqdm(comparison_partition, desc=f"Partition {letter}", leave=False)
    for record in pbar:
        if record['title'] in existing_titles:
            continue

        query = f"{record['artist']} {record['title']}"
        match = process.extractOne(query, choice_keys, scorer=fuzz.WRatio)
        if 92 <= match[1] < 100:
            matched_record = choice_mapping[match[0]]
            if matched_record['title'] == record['title']:
                continue  # Skip if titles are identical
            matches.append((record['title'], matched_record['title']))
            pbar.write(f"[{letter}] Matched: {record} to {matched_record}")

    return matches


def normalize_and_write(csv_path, choice_mapping, choice_partitions, comparison_partitions):
    """Find matching titles using partitioned processing and write results to CSV."""
    existing_titles = load_existing_titles(csv_path)
    file_is_new = not existing_titles

    # Process partitions sequentially
    all_matches = []
    letters = sorted(set(choice_partitions.keys()) | set(comparison_partitions.keys()))

    with tqdm(total=len(letters), desc="Overall Progress", unit="partition") as pbar:
        for letter in letters:
            choice_partition = choice_partitions.get(letter, [])
            comparison_partition = comparison_partitions.get(letter, [])

            if not comparison_partition or not choice_partition:
                pbar.update(1)
                continue

            matches = process_partition(letter, choice_partition, comparison_partition, choice_mapping, existing_titles)
            all_matches.extend(matches)
            pbar.update(1)

    # Write all matches to CSV
    print(f"\nWriting {len(all_matches)} matches to {csv_path}...")
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)

        if file_is_new:
            writer.writerow(["title", "title_normalized"])

        for title, normalized_title in all_matches:
            writer.writerow([title, normalized_title])

        if all_matches:
            f.flush()


def main():
    """Main entry point."""
    choices = get_choices()
    choice_mapping = create_choice_mapping(choices)
    comparison_titles = get_comparison_titles()
    csv_path = "data/title_normalized.csv"

    print(f"\nPartitioning {len(choices)} choices...")
    choice_partitions = partition_by_first_letter(choices)
    print(f"Created {len(choice_partitions)} choice partitions")

    print(f"\nPartitioning {len(comparison_titles)} comparison titles...")
    comparison_partitions = partition_by_first_letter(comparison_titles)
    print(f"Created {len(comparison_partitions)} comparison partitions")

    print("\nStarting fuzzy matching...")
    normalize_and_write(csv_path, choice_mapping, choice_partitions, comparison_partitions)
    print("\nDone!")


if __name__ == "__main__":
    main()