#!/usr/bin/env python3
"""
Data Leakage Audit for TTM Dataset
Checks for overlap with known benchmarks and calculates similarity metrics
"""

import csv
import re
import hashlib
from pathlib import Path
from collections import Counter
from typing import List, Dict, Set, Tuple

# Known benchmarks to check against
BENCHMARK_PATTERNS = {
    'MMLU': [
        r'Which of the following',
        r'Choose the correct',
        r'Select the best answer',
    ],
    'GPQA': [
        r'What is the',
        r'Which.*correct',
        r'The.*is',
    ],
    'ARC': [
        r'Which option',
        r'Choose',
    ],
    'CommonCrawl': [
        r'Question:',
        r'Answer:',
    ]
}

def load_ttm_questions() -> List[Dict]:
    """Load all TTM questions"""
    path = Path('kaggle/data/extra/ttm_mc_new.csv')
    questions = []

    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('question_type') == 'mc':
                questions.append(row)

    return questions

def extract_ngrams(text: str, n: int = 3) -> Set[str]:
    """Extract n-grams from text"""
    words = re.findall(r'\w+', text.lower())
    return {' '.join(words[i:i+n]) for i in range(len(words) - n + 1)}

def calculate_overlap(questions: List[Dict]) -> Dict:
    """Calculate various overlap metrics"""
    results = {
        'total_questions': len(questions),
        'question_length_stats': [],
        'answer_distribution': Counter(),
        'common_ngrams': Counter(),
        'pattern_matches': {},
    }

    # Question lengths
    for q in questions:
        question_text = q.get('question', '')
        results['question_length_stats'].append(len(question_text.split()))

        # Answer distribution
        answer = q.get('answer', '').upper()
        results['answer_distribution'][answer] += 1

        # N-grams
        ngrams = extract_ngrams(question_text, n=3)
        results['common_ngrams'].update(ngrams)

    # Pattern matching
    for benchmark, patterns in BENCHMARK_PATTERNS.items():
        matches = 0
        for q in questions:
            for pattern in patterns:
                if re.search(pattern, q.get('question', ''), re.IGNORECASE):
                    matches += 1
                    break
        results['pattern_matches'][benchmark] = matches

    return results

def check_exact_duplicates(questions: List[Dict]) -> List[Tuple[int, int]]:
    """Find exact duplicate questions"""
    seen = {}
    duplicates = []

    for i, q in enumerate(questions):
        text = q.get('question', '')
        # Simple hash for comparison
        h = hashlib.md5(text.lower().strip().encode()).hexdigest()

        if h in seen:
            duplicates.append((seen[h], i))
        else:
            seen[h] = i

    return duplicates

def check_near_duplicates(questions: List[Dict], threshold: float = 0.9) -> List[Tuple[int, int, float]]:
    """Find near-duplicate questions using simple overlap"""
    duplicates = []

    # Get first 100 for efficiency
    sample = questions[:100]

    for i in range(len(sample)):
        for j in range(i + 1, len(sample)):
            q1_words = set(extract_ngrams(sample[i].get('question', ''), n=2))
            q2_words = set(extract_ngrams(sample[j].get('question', ''), n=2))

            if not q1_words or not q2_words:
                continue

            intersection = len(q1_words & q2_words)
            union = len(q1_words | q2_words)

            similarity = intersection / union if union > 0 else 0

            if similarity >= threshold:
                duplicates.append((i, j, similarity))

    return duplicates

def analyze_answer_distribution(distribution: Counter) -> Dict:
    """Check if answer distribution is suspiciously uniform"""
    total = sum(distribution.values())
    expected = total / 4  # Expected if uniform

    # Chi-square test approximation
    chi_square = sum((count - expected) ** 2 / expected for count in distribution.values())

    return {
        'distribution': dict(distribution),
        'total': total,
        'expected_uniform': expected,
        'chi_square': chi_square,
        'is_suspicious': chi_square < 1.0,  # Very uniform = suspicious
        'percentages': {k: f"{v/total:.1%}" for k, v in distribution.items()}
    }

def main():
    print("=" * 70)
    print("🔍 TTM DATA LEAKAGE AUDIT")
    print("=" * 70)

    questions = load_ttm_questions()
    print(f"\n📊 Loaded {len(questions)} TTM questions")

    # Calculate overlap metrics
    print("\n" + "-" * 70)
    print("🔬 ANALYZING...")
    print("-" * 70)

    results = calculate_overlap(questions)

    # Question length stats
    avg_len = sum(results['question_length_stats']) / len(results['question_length_stats'])
    print(f"\n📏 Average question length: {avg_len:.1f} words")
    print(f"   Min: {min(results['question_length_stats'])}, Max: {max(results['question_length_stats'])}")

    # Answer distribution
    print("\n🎯 ANSWER DISTRIBUTION:")
    answer_analysis = analyze_answer_distribution(results['answer_distribution'])
    for letter, pct in answer_analysis['percentages'].items():
        print(f"   {letter}: {pct}")

    if answer_analysis['is_suspicious']:
        print("   ⚠️  Distribution is VERY uniform - possible artificial balancing")

    # Pattern matching
    print("\n🔍 PATTERN MATCHING (known benchmarks):")
    for benchmark, count in results['pattern_matches'].items():
        pct = count / len(questions) * 100
        icon = "🚨" if pct > 50 else "⚠️" if pct > 20 else "✓"
        print(f"   {icon} {benchmark}: {count} ({pct:.1f}%)")

    # Exact duplicates
    duplicates = check_exact_duplicates(questions)
    if duplicates:
        print(f"\n🚨 EXACT DUPLICATES FOUND: {len(duplicates)}")
        for i, j in duplicates[:5]:
            print(f"   Questions {i} and {j} are identical")
    else:
        print(f"\n✅ No exact duplicates found")

    # Near duplicates
    near_dups = check_near_duplicates(questions)
    if near_dups:
        print(f"\n⚠️  NEAR-DUPLICATES (90%+ similarity): {len(near_dups)}")
        for i, j, sim in near_dups[:5]:
            print(f"   Questions {i} and {j}: {sim:.1%} similar")
    else:
        print(f"\n✅ No near-duplicates found")

    # Common n-grams (could indicate template usage)
    print(f"\n📝 MOST COMMON 3-GRAMS (top 10):")
    for ngram, count in results['common_ngrams'].most_common(10):
        print(f"   '{ngram}': {count} occurrences")

    # Risk assessment
    print("\n" + "=" * 70)
    print("🎯 RISK ASSESSMENT")
    print("=" * 70)

    risk_factors = 0

    if answer_analysis['is_suspicious']:
        print("🚨 HIGH: Answer distribution too uniform (possible data generation artifact)")
        risk_factors += 1

    if any(pct > 50 for pct in [c/len(questions)*100 for c in results['pattern_matches'].values()]):
        print("🚨 HIGH: Strong pattern match with known benchmark")
        risk_factors += 1

    if len(duplicates) > 0:
        print("🚨 HIGH: Exact duplicates found")
        risk_factors += 1

    # Common patterns
    common_3gram_ratio = results['common_ngrams'].most_common(1)[0][1] / len(questions)
    if common_3gram_ratio > 0.3:
        print(f"⚠️  MEDIUM: Most common 3-gram appears in {common_3gram_ratio:.0%} of questions")
        risk_factors += 1

    if risk_factors == 0:
        print("✅ LOW RISK: No obvious leakage indicators")
    elif risk_factors == 1:
        print("⚠️  MEDIUM RISK: Some concerning indicators")
    elif risk_factors == 2:
        print("🚨 HIGH RISK: Multiple concerning indicators")
    else:
        print("🚨🚨 CRITICAL RISK: Strong evidence of data leakage")

    print("\n" + "=" * 70)
    print("📋 RECOMMENDATIONS")
    print("=" * 70)

    if risk_factors > 0:
        print("1. Create adversarial version of TTM dataset")
        print("2. Apply paraphrasing to all questions")
        print("3. Add negative constraints")
        print("4. Improve distractors (wrong answers)")
        print("5. Test with models that shouldn't have seen the data")
    else:
        print("Dataset appears clean. Consider other reasons for 100% accuracy:")
        print("- Questions may be inherently simple")
        print("- Models may have strong domain knowledge")
        print("- Prompt format may give away answers")

if __name__ == "__main__":
    main()
