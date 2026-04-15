#!/usr/bin/env python3
"""
Full audit of ALL 5 datasets - find all anomalies
"""

import csv
import re
import hashlib
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List

TRACKS = {
    'THLP': 'kaggle/data/extra/thlp_mc_new.csv',
    'TTM': 'kaggle/data/extra/ttm_mc_new.csv',
    'TAGP': 'kaggle/data/tagp_mc.csv',
    'TEFB': 'kaggle/data/extra/tefb_mc_new.csv',
    'TSCP': 'kaggle/data/extra/tscp_mc_new.csv'
}

def audit_track(track_name: str, csv_path: str) -> Dict:
    """Audit a single track for all anomalies"""
    results = {
        'track': track_name,
        'path': csv_path,
        'exists': False,
        'total_rows': 0,
        'mc_questions': 0,
        'unique_questions': 0,
        'duplicates': 0,
        'missing_fields': [],
        'invalid_answers': [],
        'answer_distribution': Counter(),
        'anomalies': [],
        'common_patterns': Counter(),
        'question_lengths': [],
        'empty_questions': 0,
        'empty_choices': 0,
        'invalid_choice_format': 0
    }

    path = Path(csv_path)
    if not path.exists():
        results['anomalies'].append(f"❌ FILE NOT FOUND: {csv_path}")
        return results

    results['exists'] = True

    try:
        with open(path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            results['total_rows'] = len(rows)

            # Check for missing fields
            if rows:
                required = ['id', 'question_type', 'question', 'choices', 'answer']
                for field in required:
                    missing = [i for i, row in enumerate(rows) if not row.get(field)]
                    if missing:
                        results['missing_fields'].append(f"{field}: {len(missing)} rows")

            # Track unique questions
            question_hashes = defaultdict(list)
            choice_hashes = defaultdict(list)

            for i, row in enumerate(rows):
                # Only MC questions
                if row.get('question_type', '').lower() != 'mc':
                    continue

                results['mc_questions'] += 1

                # Get question text
                question = row.get('question', '')
                choices = row.get('choices', '')
                answer = row.get('answer', '').upper().strip()

                # Empty checks
                if not question or question.strip() == '':
                    results['empty_questions'] += 1
                if not choices or choices.strip() == '':
                    results['empty_choices'] += 1

                # Question length
                results['question_lengths'].append(len(question.split()) if question else 0)

                # Answer validation
                if answer not in ['A', 'B', 'C', 'D']:
                    results['invalid_answers'].append(f"Row {i}: {answer}")

                # Answer distribution
                results['answer_distribution'][answer] += 1

                # Hash for uniqueness
                q_hash = hashlib.md5(question.lower().strip().encode()).hexdigest()
                question_hashes[q_hash].append(i)

                c_hash = hashlib.md5(choices.lower().strip().encode()).hexdigest()
                choice_hashes[c_hash].append(i)

                # Common n-grams
                words = re.findall(r'\w+', question.lower())
                for n in [2, 3]:
                    for j in range(len(words) - n + 1):
                        ngram = ' '.join(words[j:j+n])
                        results['common_patterns'][ngram] += 1

            # Unique questions
            results['unique_questions'] = len(question_hashes)

            # Duplicates
            dup_questions = sum(len(v) - 1 for v in question_hashes.values() if len(v) > 1)
            results['duplicates'] = dup_questions

            # Check for choice format issues
            for i, row in enumerate(rows):
                if row.get('question_type', '').lower() != 'mc':
                    continue
                choices = row.get('choices', '')
                # Should have A) B) C) D) pattern
                if choices and not re.search(r'[ABCD]\)', choices):
                    results['invalid_choice_format'] += 1

            # Anomaly detection
            # 1. High duplicate rate
            dup_rate = results['duplicates'] / results['mc_questions'] if results['mc_questions'] > 0 else 0
            if dup_rate > 0.5:
                results['anomalies'].append(f"🚨 HIGH DUPLICATE RATE: {dup_rate:.1%}")

            # 2. Suspicious answer distribution (too uniform)
            if len(results['answer_distribution']) == 4:
                counts = list(results['answer_distribution'].values())
                expected = results['mc_questions'] / 4
                chi_square = sum((c - expected)**2 / expected for c in counts)
                if chi_square < 1.0:
                    results['anomalies'].append(f"⚠️  ARTIFICIALLY UNIFORM ANSWERS (chi²={chi_square:.2f})")

            # 3. Empty content
            if results['empty_questions'] > 0:
                results['anomalies'].append(f"🚨 {results['empty_questions']} EMPTY QUESTIONS")
            if results['empty_choices'] > 0:
                results['anomalies'].append(f"🚨 {results['empty_choices']} EMPTY CHOICES")

            # 4. Invalid answers
            if results['invalid_answers']:
                results['anomalies'].append(f"⚠️  {len(results['invalid_answers'])} INVALID ANSWERS")

            # 5. Invalid choice format
            if results['invalid_choice_format'] > 0:
                results['anomalies'].append(f"⚠️  {results['invalid_choice_format']} INVALID CHOICE FORMAT")

            # 6. Common pattern domination
            if results['common_patterns']:
                top_pattern, count = results['common_patterns'].most_common(1)[0]
                pattern_rate = count / results['mc_questions'] if results['mc_questions'] > 0 else 0
                if pattern_rate > 0.3:
                    results['anomalies'].append(f"⚠️  DOMINANT PATTERN: '{top_pattern}' in {pattern_rate:.0%} of Qs")

            # 7. Low unique count
            if results['unique_questions'] < results['mc_questions'] * 0.1:
                results['anomalies'].append(f"🚨 VERY LOW UNIQUENESS: {results['unique_questions']}/{results['mc_questions']}")

    except Exception as e:
        results['anomalies'].append(f"❌ ERROR: {str(e)}")

    return results

def main():
    print("=" * 80)
    print("🔍 FULL AUDIT OF ALL 5 DATASETS")
    print("=" * 80)

    all_results = []

    for track, path in TRACKS.items():
        print(f"\n{'─' * 80}")
        print(f"📋 {track}")
        print(f"{'─' * 80}")

        result = audit_track(track, path)
        all_results.append(result)

        if not result['exists']:
            print(f"❌ File not found: {path}")
            continue

        print(f"📊 Total rows: {result['total_rows']}")
        print(f"📊 MC questions: {result['mc_questions']}")
        print(f"🔢 Unique questions: {result['unique_questions']}")
        print(f"🔄 Duplicates: {result['duplicates']}")
        print(f"📏 Avg question length: {sum(result['question_lengths'])/len(result['question_lengths']) if result['question_lengths'] else 0:.1f} words")

        print(f"\n🎯 Answer distribution:")
        for letter in sorted(result['answer_distribution'].keys()):
            count = result['answer_distribution'][letter]
            pct = count / result['mc_questions'] * 100 if result['mc_questions'] > 0 else 0
            print(f"   {letter}: {count} ({pct:.1f}%)")

        if result['anomalies']:
            print(f"\n🚨 ANOMALIES ({len(result['anomalies'])}):")
            for anomaly in result['anomalies']:
                print(f"   {anomaly}")
        else:
            print(f"\n✅ No anomalies detected")

    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY TABLE")
    print("=" * 80)

    print(f"{'Track':<6} | {'Total':<6} | {'MC':<5} | {'Unique':<7} | {'Dup':<5} | {'Anomalies':<10}")
    print("-" * 80)

    for r in all_results:
        anomaly_count = len(r['anomalies']) if r['exists'] else 1
        anomaly_indicator = "🚨" if anomaly_count > 0 else "✅"
        unique_ratio = f"{r['unique_questions']}/{r['mc_questions']}" if r['exists'] else "N/A"
        dup_pct = f"{r['duplicates']}/{r['mc_questions']}" if r['mc_questions'] > 0 else "N/A"

        print(f"{r['track']:<6} | {str(r['total_rows']):<6} | {str(r['mc_questions']):<5} | {unique_ratio:<7} | {dup_pct:<5} | {anomaly_indicator} {anomaly_count}")

    print("=" * 80)

    # Fix recommendations
    print("\n🔧 FIX RECOMMENDATIONS:")
    print("=" * 80)

    tracks_to_fix = []
    for r in all_results:
        if r['anomalies']:
            tracks_to_fix.append(r['track'])
            print(f"\n{r['track']}:")
            for a in r['anomalies']:
                print(f"  - {a}")
        elif not r['exists']:
            tracks_to_fix.append(r['track'])
            print(f"\n{r['track']}: FILE MISSING")

    if tracks_to_fix:
        print(f"\n⚡ TRACKS NEEDING FIXES: {', '.join(tracks_to_fix)}")
    else:
        print(f"\n✅ ALL DATASETS CLEAN")

    print("=" * 80)

if __name__ == "__main__":
    main()
