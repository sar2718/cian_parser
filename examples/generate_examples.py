#!/usr/bin/env python3
"""
Script for generating example data and statistics.
Uses source files from Downloads and creates examples/ structure.
"""

import json
import shutil
from pathlib import Path

# Paths to source files
SOURCE_DIR = Path("C:/Users/SAR/Downloads")
UNIQUE_JSON = SOURCE_DIR / "unique.json"
DISTRICT_STATS = SOURCE_DIR / "district_stats.json"
VISUALIZATIONS = [
    "hist_total_price.png",
    "hist_price_m2.png",
    "boxplot_price_m2_by_rooms.png",
]

# Target directories
EXAMPLES_DIR = Path(__file__).parent
DATA_DIR = EXAMPLES_DIR / "data"
VIZ_DIR = EXAMPLES_DIR / "visualizations"


def main():
    # Create directory structure
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    VIZ_DIR.mkdir(parents=True, exist_ok=True)

    # Copy data
    print("Copying data...")
    shutil.copy(UNIQUE_JSON, DATA_DIR / "unique.json")
    shutil.copy(DISTRICT_STATS, DATA_DIR / "district_stats.json")

    # Copy visualizations
    print("Copying visualizations...")
    for viz in VISUALIZATIONS:
        src = SOURCE_DIR / viz
        if src.exists():
            shutil.copy(src, VIZ_DIR / viz)
            print(f"  OK {viz}")
        else:
            print(f"  MISSING {viz}")

    # Print statistics
    with open(DATA_DIR / "unique.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        print(f"\nCopied {len(data)} listings")

    print("\nExamples generated successfully!")


if __name__ == "__main__":
    main()
