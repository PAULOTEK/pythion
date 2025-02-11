#!/usr/bin/env python

import requests
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# URL and authentication
URL = 'https://siem.muevy.com/_cat/allocation?v=true'
INDEX_URL = 'https://siem.muevy.com/_cat/indices?v=true'
AUTH = ('aesadmin', 'gjqC@0n46n6>')  # Username and password
TIMEOUT = 10  # Request timeout in seconds

def fetch_data(url, auth):
    """Makes a GET request to fetch data."""
    try:
        response = requests.get(url, auth=auth, timeout=TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Connection error: {e}")
        return None

def parse_disk_size(size_str):
    """Converts disk size strings (with suffixes) and returns the converted value and original unit."""
    if not size_str or size_str == '-':
        return 0, "0 B"
    size = float(size_str[:-2])
    unit = size_str[-2:].lower()
    unit_multipliers = {'kb': 1 / 1024, 'mb': 1, 'gb': 1024, 'tb': 1024**2}
    converted_size = size * unit_multipliers.get(unit, 1)
    return converted_size, f"{size} {unit.upper()}"

def format_size(size_mb):
    """Formats size to the most appropriate unit."""
    if size_mb >= 1024:
        return f"{size_mb / 1024:.2f} GB"
    elif size_mb >= 1:
        return f"{size_mb:.2f} MB"
    else:
        return f"{size_mb * 1024:.2f} KB"

def parse_index_data(data):
    """Displays index information and sums totals by prefix and specific categories."""
    lines = data.splitlines()
    if len(lines) <= 1:
        logging.info("No relevant data found in indices.")
        return

    header = lines[0].split()
    rows = lines[1:]
    indices = {col: header.index(col) for col in header}

    total_disk_size = 0
    category_totals = defaultdict(float)
    specific_totals = {"cwl-": 0, "log-ocsf-identity": 0, "metrics-opensearch-index": 0,
                       "log-ocsf-findings": 0, "log-ocsf-network": 0, "log-ocsf-application": 0}

    for row in rows:
        columns = row.split()
        index_name = columns[indices['index']]
        converted_size, original_str = parse_disk_size(columns[indices['store.size']])
        total_disk_size += converted_size

        category = index_name.split('-')[0]
        category_totals[category] += converted_size

        for key in specific_totals.keys():
            if index_name.startswith(key):
                specific_totals[key] += converted_size

    logging.info("\n--- Totals by Category ---")
    for category, size in category_totals.items():
        logging.info(f"{category}: {format_size(size)}")
    logging.info("-" * 40)

    logging.info("\n--- Totals by Specific Category ---")
    for key, size in specific_totals.items():
        logging.info(f"{key}: {format_size(size)}")
    logging.info("-" * 40)

    logging.info("\n--- Total Indices ---")
    logging.info(f"Total index size: {format_size(total_disk_size)}")
    logging.info("-" * 40)

def main():
    index_data = fetch_data(INDEX_URL, AUTH)
    if index_data:
        parse_index_data(index_data)

if __name__ == "__main__":
    main()
#