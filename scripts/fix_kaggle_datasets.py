#!/usr/bin/env python3
"""
Fix Kaggle Datasets for AGI Hackathon
Applies all necessary fixes to ensure dataset compatibility
"""

import csv
import re
from pathlib import Path
from typing import List, Dict

# File paths
DATA_DIR = Path(__file__).parent.parent / "kaggle" / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "kaggle" / "data"

TRACKS = ["thlp", "ttm", "tagp", "tefb", "tscp"]


def read_csv_safe(file_path: Path) -> List[Dict]:
    """Safely read CSV with proper encoding"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []


def write_csv_safe(file_path: Path, rows: List[Dict], fieldnames: List[str]):
    """Safely write CSV with UTF-8 encoding"""
    try:
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}")
        return False


def fix_thlp(data: List[Dict]) -> List[Dict]:
    """Fix THLP dataset: flatten multiline choice text"""
    print("Fixing THLP: flattening multiline choices...")

    fixed = []
    for row in data:
        # Flatten multiline text in choices
        for choice in ['A', 'B', 'C', 'D']:
            if row.get(choice):
                # Replace newlines and tabs with spaces
                row[choice] = re.sub(r'[\n\r\t]+', ' ', str(row[choice])).strip()

        # Validate answer
        answer = row.get('answer', '').strip().upper()
        if answer not in ['A', 'B', 'C', 'D']:
            # Skip invalid rows
            continue

        fixed.append(row)

    print(f"  {len(fixed)} valid rows (from {len(data)})")
    return fixed


def fix_ttm(data: List[Dict]) -> List[Dict]:
    """Fix TTM dataset: handle encoding issues"""
    print("Fixing TTM: normalizing encoding...")

    fixed = []
    for row in data:
        # Normalize unicode
        for key in row:
            if row[key]:
                row[key] = row[key].encode('utf-8', 'ignore').decode('utf-8')
                # Normalize quotes
                row[key] = row[key].replace('"', '"').replace(''', "'")

        # Validate answer
        answer = row.get('answer', '').strip().upper()
        if answer not in ['A', 'B', 'C', 'D']:
            continue

        fixed.append(row)

    print(f"  {len(fixed)} valid rows (from {len(data)})")
    return fixed


def fix_tagp(data: List[Dict]) -> List[Dict]:
    """Fix TAGP dataset: normalize special characters"""
    print("Fixing TAGP: normalizing special characters...")

    fixed = []
    for row in data:
        # Normalize special characters
        for key in row:
            if row[key]:
                # Unicode normalization
                row[key] = row[key].encode('utf-8', 'ignore').decode('utf-8')
                # Escape markdown characters
                row[key] = row[key].replace('*', '\\*')

        # Validate answer
        answer = row.get('answer', '').strip().upper()
        if answer not in ['A', 'B', 'C', 'D']:
            continue

        fixed.append(row)

    print(f"  {len(fixed)} valid rows (from {len(data)})")
    return fixed


def fix_tefb(data: List[Dict]) -> List[Dict]:
    """Fix TEFB dataset: standardize answer format"""
    print("Fixing TEFB: standardizing answer format...")

    fixed = []
    for row in data:
        # Normalize answer format
        answer = row.get('answer', '').strip().upper()

        # Remove prefixes like "(A)" or "Answer: A"
        answer = re.sub(r'^[\(\[].*?[\)\]]\s*', '', answer)
        answer = re.sub(r'^(Answer|answer):\s*', '', answer)
        answer = answer.strip()

        # Extract just the letter
        match = re.search(r'([ABCD])', answer)
        if match:
            answer = match.group(1)

        # Validate
        if answer not in ['A', 'B', 'C', 'D']:
            continue

        row['answer'] = answer
        fixed.append(row)

    print(f"  {len(fixed)} valid rows (from {len(data)})")
    return fixed


def fix_tscp(data: List[Dict]) -> List[Dict]:
    """Fix TSCP dataset: standardize CSV delimiters"""
    print("Fixing TSCP: validating structure...")

    fixed = []
    for row in data:
        # Ensure all required fields exist
        if not all(k in row for k in ['id', 'question', 'answer', 'A', 'B', 'C', 'D']):
            continue

        # Validate answer
        answer = row.get('answer', '').strip().upper()
        if answer not in ['A', 'B', 'C', 'D']:
            continue

        # Clean up fields
        for key in row:
            if isinstance(row[key], str):
                row[key] = row[key].strip()

        fixed.append(row)

    print(f"  {len(fixed)} valid rows (from {len(data)})")
    return fixed


FIX_FUNCTIONS = {
    'thlp': fix_thlp,
    'ttm': fix_ttm,
    'tagp': fix_tagp,
    'tefb': fix_tefb,
    'tscp': fix_tscp
}


def fix_track(track: str) -> bool:
    """Fix a single track dataset"""
    print(f"\n{'='*60}")
    print(f"Fixing {track.upper()} dataset")
    print(f"{'='*60}")

    # Find input file
    input_files = list(DATA_DIR.glob(f"{track}*.csv"))
    if not input_files:
        print(f"No input file found for {track}")
        return False

    input_file = input_files[0]
    print(f"Reading: {input_file}")

    # Read data
    data = read_csv_safe(input_file)
    if not data:
        print("No data read from file")
        return False

    # Apply fix
    fix_func = FIX_FUNCTIONS.get(track)
    if not fix_func:
        print(f"No fix function for {track}")
        return False

    fixed_data = fix_func(data)

    # Write output
    output_file = OUTPUT_DIR / f"{track}_mc_fixed.csv"
    if write_csv_safe(output_file, fixed_data, data[0].keys()):
        print(f"✅ Written to: {output_file}")
        return True
    else:
        print("❌ Failed to write output")
        return False


def main():
    """Main function"""
    print("="*60)
    print("Kaggle Dataset Fix Utility")
    print("="*60)

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Fix all tracks
    results = {}
    for track in TRACKS:
        results[track] = fix_track(track)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    for track, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {track.upper()}: {'Success' if success else 'Failed'}")


if __name__ == "__main__":
    main()
