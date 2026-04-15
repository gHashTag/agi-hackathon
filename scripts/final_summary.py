#!/usr/bin/env python3
"""
Final summary of cleaned datasets
"""

import csv
from pathlib import Path

CLEANED_DATASETS = {
    'THLP': 'kaggle/data/extra/thlp_mc_cleaned.csv',
    'TTM': 'kaggle/data/extra/ttm_mc_adversarial_v3.csv',  # Use adversarial
    'TAGP': 'kaggle/data/tagp_mc_cleaned.csv',
    'TEFB': 'kaggle/data/extra/tefb_mc_cleaned.csv',
    'TSCP': 'kaggle/data/extra/tscp_mc_cleaned.csv',
}

def get_stats(csv_path: str) -> dict:
    """Get statistics for a dataset"""
    path = Path(csv_path)
    if not path.exists():
        return {'exists': False}

    questions = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('question_type', '').lower() == 'mc':
                questions.append(row)

    answer_dist = {}
    for q in questions:
        a = q.get('answer', '').upper()
        answer_dist[a] = answer_dist.get(a, 0) + 1

    return {
        'exists': True,
        'total_questions': len(questions),
        'answer_distribution': answer_dist,
    }

def main():
    print("=" * 70)
    print("📊 FINAL DATASET SUMMARY (CLEANED)")
    print("=" * 70)

    total_questions = 0

    print(f"\n{'Track':<6} | {'Questions':<10} | {'A':<5} | {'B':<5} | {'C':<5} | {'D':<5}")
    print("-" * 70)

    for track, path in CLEANED_DATASETS.items():
        stats = get_stats(path)

        if not stats['exists']:
            print(f"{track:<6} | ❌ NOT FOUND")
            continue

        q_count = stats['total_questions']
        total_questions += q_count

        a = stats['answer_distribution'].get('A', 0)
        b = stats['answer_distribution'].get('B', 0)
        c = stats['answer_distribution'].get('C', 0)
        d = stats['answer_distribution'].get('D', 0)

        print(f"{track:<6} | {q_count:<10} | {a:<5} | {b:<5} | {c:<5} | {d:<5}")

    print("-" * 70)
    print(f"{'TOTAL':<6} | {total_questions:<10}")
    print("=" * 70)

    print("\n📁 CLEANED FILES:")
    for track, path in CLEANED_DATASETS.items():
        if Path(path).exists():
            print(f"   ✅ {path}")

    print("\n🎯 READY FOR:")
    print("   1. Kaggle notebook upload")
    print("   2. Model evaluation")
    print("   3. Leaderboard competition")
    print("=" * 70)

if __name__ == "__main__":
    main()
