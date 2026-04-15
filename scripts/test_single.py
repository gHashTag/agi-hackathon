#!/usr/bin/env python3
"""
Quick test script - evaluate a single question on a real model
For testing evaluation pipeline before hackathon
"""

import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Question:
    id: str
    question_type: str
    question: str
    choices: list[str]
    answer: str


def load_example_question(track_dir: str) -> Question:
    """Load a single example question from track directory"""
    import csv

    csv_files = list(Path(track_dir).glob("*.csv"))
    if not csv_files:
        print(f"Error: No CSV files found in {track_dir}")
        return None

    with open(csv_files[0], 'r') as f:
        reader = csv.DictReader(f)

        # Read first 5 rows as examples
        for i, row in enumerate(reader):
            if i >= 5:  # Skip header + 4 examples
                break

            if i >= 1:  # Use 1-4 as examples (skip header)
                print(f"
{'='*60}")
                print(f"Example {i-1}:")
                print(f"ID: {row.get('id', 'N/A')}")
                print(f"Type: {row.get('question_type', 'N/A')}")
                print(f"Question: {row.get('question', 'N/A')}")
                print(f"Choices:")
                for letter in ['A', 'B', 'C', 'D']:
                    choice = row.get(letter, '')
                    if choice:
                        print(f"  {letter}) {choice}")
                print(f"Answer: {row.get('answer', 'N/A')}")
                print(f"{'='*60}")

                # Return as Question object
                return Question(
                    id=row.get('id', ''),
                    question_type=row.get('question_type', ''),
                    question=row.get('question', ''),
                    choices=[row.get('A', ''), row.get('B', ''), row.get('C', ''), row.get('D', '')],
                    answer=row.get('answer', '')
                )

    return None


def print_test_prompt(question: Question):
    """Print a formatted test prompt"""
    print(f"
{'='*60}")
    print(f"{'='*60}")
    print(f"Test Question for {question.question_type}")
    print(f"{'='*60}")
    print(f"
Question: {question.question}")
    print(f"
Choices:")
    for i, choice in enumerate(question.choices):
        if choice:  # Only show non-empty choices
            print(f"  {['A', 'B', 'C', 'D'][i]}) {choice}")
    print(f"
Answer: {question.answer} (do not share with model!)")
    print(f"{'='*60}
")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python test_single.py --track <thlp|ttm|tagp|tefb|tscp>")
        print("
Example:")
        print("  python test_single.py --track thlp")
        sys.exit(1)

    track = sys.argv[2]

    # Track mapping
    tracks = {
        'thlp': 'THLP - Pattern Learning',
        'ttm': 'TTM - Metacognitive Calibration',
        'tagp': 'TAGP - Attention',
        'tefb': 'TEFB - Executive Functions',
        'tscp': 'TSCP - Social Cognition'
    }

    if track not in tracks:
        print(f"Error: Unknown track '{track}'")
        print(f"Valid tracks: {', '.join(tracks.keys())}")
        sys.exit(1)

    # Find track directory (relative to project root)
    base_dir = Path(__file__).parent.parent / "data" / track
    if not base_dir.exists():
        print(f"Error: Track directory not found at {base_dir}")
        print("Please run: bash scripts/download_data.sh")
        sys.exit(1)

    # Load example question
    question = load_example_question(str(base_dir))

    if not question:
        print("Error: Could not load example question")
        sys.exit(1)

    print(f"
{'='*60}")
    print(f"Loaded example from: {tracks[track]}")
    print(f"Track: {track}")
    print(f"{'='*60}
")

    # Print test prompt
    print_test_prompt(question)


if __name__ == "__main__":
    main()
