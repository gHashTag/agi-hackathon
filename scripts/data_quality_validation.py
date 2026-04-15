#!/usr/bin/env python3
"""
Data Quality Validation for Trinity Cognitive Probes

Checks:
1. Duplicate detection
2. Answer distribution analysis
3. Adversarial quality assessment
4. Question similarity analysis
"""

import pandas as pd
import json
import csv
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from typing import Dict, List, Tuple

# Dataset paths
DATASETS = {
    "thlp_mc_adversarial": "kaggle/data/extra/thlp_mc_adversarial.csv",
    "ttm_physics_mc": "kaggle/data/extra/ttm_physics_mc.csv",
    "tagp_mc_adversarial": "kaggle/data/tagp_mc_aggressive.csv",
    "tefb_mc_cleaned": "kaggle/data/extra/tefb_mc_cleaned.csv",
    "tscp_mc_cleaned": "kaggle/data/extra/tscp_mc_cleaned.csv"
}

def load_dataset(dataset_path: str) -> pd.DataFrame:
    """Load dataset and perform basic validation"""
    df = pd.read_csv(dataset_path)

    # Basic validation
    if 'question' not in df.columns:
        print(f"⚠️ No 'question' column in {dataset_path}")
        return None

    if 'choices' not in df.columns:
        print(f"⚠️ No 'choices' column in {dataset_path}")
        return None

    if 'answer' not in df.columns:
        print(f"⚠️ No 'answer' column in {dataset_path}")
        return None

    return df

def detect_duplicates(df: pd.DataFrame) -> Dict[str, any]:
    """Detect duplicate questions and answer patterns"""
    report = {}

    # Exact duplicates (question text)
    df_clean = df.dropna(subset=['question'])
    question_counts = df_clean['question'].value_counts()
    duplicates = question_counts[question_counts > 1]

    report['exact_question_duplicates'] = len(duplicates)

    if len(duplicates) > 0:
        print(f"\n🔍 Found {len(duplicates)} duplicate question(s):")
        for q, count in duplicates.head(5).items():
            print(f"  - \"{q[:60]}...\" ({count} copies)")

    # Answer pattern duplicates
    answer_patterns = df_clean['choices'].apply(lambda x: '|'.join(sorted(x.split('|'))))
    pattern_counts = answer_patterns.value_counts()
    dup_patterns = pattern_counts[pattern_counts > 1]

    report['answer_pattern_duplicates'] = len(dup_patterns)

    if len(dup_patterns) > 0:
        print(f"\n🔍 Found {len(dup_patterns)} duplicate answer pattern(s):")
        for pattern, count in dup_patterns.head(5).items():
            print(f"  - \"{pattern[:80]}...\" ({count} copies)")

    # Semantic duplicates (simplified)
    def normalize_text(text: str) -> str:
        """Normalize text for duplicate detection"""
        return ' '.join(text.lower().replace('[^a-z0-9\s]', ' ').split())

    df_clean['normalized'] = df_clean['question'].apply(normalize_text)
    norm_counts = df_clean['normalized'].value_counts()
    norm_dupes = norm_counts[norm_counts > 1]

    report['semantic_duplicates'] = len(norm_dupes)

    if len(norm_dupes) > 0:
        print(f"\n🔍 Found {len(norm_dupes)} potentially semantic duplicate(s):")
        for q, count in norm_dupes.head(3).items():
            print(f"  - \"{q[:60]}...\" ({count} similar)")

    return report

def analyze_answer_distribution(df: pd.DataFrame) -> Dict[str, any]:
    """Analyze distribution of answers (A, B, C, D)"""
    report = {}

    # Clean answers
    df_clean = df.dropna(subset=['answer'])

    if df_clean.empty:
        report['total_questions'] = 0
        return report

    # Extract answers
    def parse_answer(ans: str) -> str:
        """Parse answer from various formats"""
        ans = str(ans).strip().upper()
        # Remove non-letter characters
        return ''.join(c for c in ans if c.isalpha())

    df_clean['parsed_answer'] = df_clean['answer'].apply(parse_answer)

    # Filter valid answers (A, B, C, D)
    valid_answers = df_clean[df_clean['parsed_answer'].isin(['A', 'B', 'C', 'D'])]

    if valid_answers.empty:
        report['total_questions'] = len(df_clean)
        report['valid_answers'] = 0
        report['invalid_answers'] = len(df_clean)
        return report

    # Distribution
    answer_dist = valid_answers['parsed_answer'].value_counts(normalize=True)
    report['answer_distribution'] = {k: f"{v:.1%}" for k, v in answer_dist.items()}
    report['total_questions'] = len(df_clean)
    report['valid_answers'] = len(valid_answers)
    report['invalid_answers'] = len(df_clean) - len(valid_answers)

    # Check for uniform distribution (ideal for adversarial)
    ideal_distribution = {k: 0.25 for k in ['A', 'B', 'C', 'D']}

    # Calculate KL divergence from uniform
    observed = {k: v/100 for k, v in answer_dist.items()}
    kl_divergence = sum(k * np.log2(k / 0.25) for k, k in observed.items())

    report['kl_divergence_uniform'] = kl_divergence
    report['is_uniform'] = kl_divergence < 0.1

    # Visual answer distribution
    if report['total_questions'] > 0:
        print(f"\n📊 Answer Distribution:")
        for answer in ['A', 'B', 'C', 'D']:
            count = answer_dist.get(answer, 0)
            percent = count * 100
            print(f"  {answer}: {percent:.1f}% ({count} questions)")

        print(f"\n📈 KL Divergence from Uniform: {kl_divergence:.3f}")
        print(f"Uniform Distribution: {'✅ Good' if report['is_uniform'] else '⚠️ Biased'}")

    return report

def assess_adversarial_quality(df: pd.DataFrame) -> Dict[str, any]:
    """Assess quality of adversarial questions"""
    report = {}

    if df.empty:
        return report

    # Check for adversarial techniques
    text = ' '.join(df['question'].astype(str).tolist()).lower()

    adversarial_indicators = {
        'negative_constraint': ['not', 'avoid', 'incorrect', 'false', 'wrong'],
        'paraphrasing': ['however', 'although', 'despite', 'consider'],
        'trick_questions': ['trick', 'puzzle', 'confuse', 'mislead'],
        'complex_reasoning': ['step by step', 'reasoning chain', 'multi-step'],
        'counterintuitive': ['surprising', 'unexpected', 'unlikely', 'contrary']
    }

    found_indicators = []
    for indicator, keywords in adversarial_indicators.items():
        count = sum(text.count(kw) for kw in keywords)
        if count > 0:
            found_indicators.append((indicator, count))

    report['adversarial_indicators'] = {k: v for k, v in found_indicators}
    report['adversarial_score'] = len(found_indicators)

    if len(found_indicators) > 0:
        print(f"\n🎭 Adversarial Quality Analysis:")
        for indicator, count in found_indicators:
            print(f"  ✅ {indicator}: {count} instances")
    else:
        print(f"\n⚠️ No adversarial indicators found")

    # Question length analysis
    df['question_length'] = df['question'].astype(str).str.len()
    avg_length = df['question_length'].mean()
    median_length = df['question_length'].median()

    report['avg_question_length'] = avg_length
    report['median_question_length'] = median_length

    print(f"\n📏 Question Length:")
    print(f"  Average: {avg_length:.1f} characters")
    print(f"  Median: {median_length:.1f} characters")

    # Choices complexity
    def analyze_choices(choices: str) -> Dict[str, any]:
        """Analyze complexity of answer choices"""
        options = choices.split('|')

        return {
            'num_choices': len(options),
            'avg_choice_length': sum(len(opt) for opt in options) / len(options),
            'unique_choices': len(set(options))
        }

    df['choices_analysis'] = df['choices'].apply(analyze_choices)

    report['avg_num_choices'] = df['choices_analysis'].apply(lambda x: x['num_choices']).mean()
    report['avg_choice_length'] = df['choices_analysis'].apply(lambda x: x['avg_choice_length']).mean()

    print(f"\n📋 Choices Complexity:")
    print(f"  Average Options: {report['avg_num_choices']:.2f}")
    print(f"  Average Choice Length: {report['avg_choice_length']:.1f} characters")

    return report

def generate_quality_report(datasets: Dict[str, str]) -> str:
    """Generate comprehensive quality report"""
    report_lines = []

    report_lines.append("=" * 80)
    report_lines.append("DATA QUALITY VALIDATION REPORT")
    report_lines.append("Trinity Cognitive Probes - Adversarial Datasets")
    report_lines.append("=" * 80)
    report_lines.append("")

    # Summary table
    report_lines.append("## SUMMARY")
    report_lines.append("")
    report_lines.append("| Dataset | Questions | Duplicates | Uniform | Adversarial | Quality |")
    report_lines.append("|----------|-----------|------------|---------|------------|----------|----------|")

    for name, path in datasets.items():
        if not Path(path).exists():
            print(f"⚠️ Skipping {name}: {path} not found")
            continue

        print(f"\n{'=' * 40}")
        print(f"Analyzing {name}")
        print(f"{'=' * 40}")

        df = load_dataset(path)
        if df is None:
            report_lines.append(f"| {name:<20} | {'N/A':>9} | {'ERROR':>8} | {'ERROR':>8} | {'ERROR':>8} | {'ERROR':>8} |")
            continue

        # Run all analyses
        dup_report = detect_duplicates(df)
        dist_report = analyze_answer_distribution(df)
        adv_report = assess_adversarial_quality(df)

        # Summary row
        dup_count = sum(v for v in dup_report.values())
        is_uniform = "✅" if dist_report.get('is_uniform', False) else "⚠️"
        adv_score = adv_report.get('adversarial_score', 0)
        quality = "✅ Good" if adv_score >= 3 and dist_report.get('kl_divergence_uniform', 1) < 0.3 else "⚠️ Needs Work"

        report_lines.append(f"| {name:<20} | {dist_report.get('total_questions', 0):>9} | {dup_count:>8} | {is_uniform:>8} | {adv_score:>8} | {quality:>8} |")

    report_lines.append("")
    report_lines.append("## DETAILED ANALYSIS")
    report_lines.append("")

    # Detailed analysis for each dataset
    for name, path in datasets.items():
        if not Path(path).exists():
            continue

        report_lines.append(f"### {name.replace('_', ' ').title()}")
        report_lines.append("")

        df = load_dataset(path)
        if df is None:
            continue

        # Duplicates
        dup_report = detect_duplicates(df)
        report_lines.append(f"**Duplicates:**")
        report_lines.append(f"- Exact: {dup_report.get('exact_question_duplicates', 0)}")
        report_lines.append(f"- Answer Patterns: {dup_report.get('answer_pattern_duplicates', 0)}")
        report_lines.append(f"- Semantic: {dup_report.get('semantic_duplicates', 0)}")
        report_lines.append("")

        # Answer Distribution
        dist_report = analyze_answer_distribution(df)
        report_lines.append(f"**Answer Distribution:**")
        report_lines.append(f"- Total Questions: {dist_report.get('total_questions', 0)}")
        report_lines.append(f"- Valid Answers: {dist_report.get('valid_answers', 0)}")
        report_lines.append(f"- Invalid Answers: {dist_report.get('invalid_answers', 0)}")

        for answer, pct in dist_report.get('answer_distribution', {}).items():
            report_lines.append(f"- {answer}: {pct}")

        report_lines.append(f"- KL Divergence: {dist_report.get('kl_divergence_uniform', 0):.3f}")
        report_lines.append(f"- Uniform: {'✅ Yes' if dist_report.get('is_uniform', False) else '⚠️ No'}")
        report_lines.append("")

        # Adversarial Quality
        adv_report = assess_adversarial_quality(df)
        report_lines.append(f"**Adversarial Quality:**")
        report_lines.append(f"- Adversarial Indicators: {adv_report.get('adversarial_score', 0)}")

        for indicator, count in adv_report.get('adversarial_indicators', {}).items():
            report_lines.append(f"  - {indicator}: {count} instances")

        report_lines.append("")

        # Question Complexity
        report_lines.append(f"**Question Complexity:**")
        report_lines.append(f"- Average Length: {adv_report.get('avg_question_length', 0):.1f} chars")
        report_lines.append(f"- Median Length: {adv_report.get('median_question_length', 0):.1f} chars")
        report_lines.append(f"- Average Choices: {adv_report.get('avg_num_choices', 0):.2f}")
        report_lines.append(f"- Average Choice Length: {adv_report.get('avg_choice_length', 0):.1f} chars")
        report_lines.append("")
        report_lines.append("-" * 60)

    # Recommendations
    report_lines.append("## RECOMMENDATIONS")
    report_lines.append("")
    report_lines.append("### General")
    report_lines.append("- ✅ All datasets should have < 5% duplicates")
    report_lines.append("- ✅ Answer distribution should be close to uniform (KL < 0.3)")
    report_lines.append("- ✅ Adversarial indicators: 3+ for robust evaluation")
    report_lines.append("")

    report_lines.append("### Per-Dataset")
    report_lines.append("- **THLP**: Target 25-40% accuracy, needs strong adversarial")
    report_lines.append("- **TTM**: Physics enhanced, target 10-25% accuracy")
    report_lines.append("- **TAGP**: Abstract reasoning, target 20-35% accuracy")
    report_lines.append("- **TEFB**: Executive function, target 50-70% accuracy")
    report_lines.append("- **TSCP**: Small dataset (25 Q), target 60-80% accuracy")

    return '\n'.join(report_lines)

def main():
    """Main execution function"""
    # Generate report
    report = generate_quality_report(DATASETS)

    # Save report
    report_path = Path('kaggle/data') / 'data_quality_report.md'

    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\n📄 Report saved to: {report_path}")

    # Save as CSV for easy viewing
    summary_path = Path('kaggle/data') / 'quality_summary.csv'

    summary_data = []
    for name, path in DATASETS.items():
        if not Path(path).exists():
            continue

        try:
            df = load_dataset(path)
            if df is None:
                continue

            dup_report = detect_duplicates(df)
            dist_report = analyze_answer_distribution(df)
            adv_report = assess_adversarial_quality(df)

            summary_data.append({
                'dataset': name,
                'questions': dist_report.get('total_questions', 0),
                'duplicates': sum(v for v in dup_report.values()),
                'uniform_distribution': dist_report.get('is_uniform', False),
                'kl_divergence': dist_report.get('kl_divergence_uniform', 0),
                'adversarial_score': adv_report.get('adversarial_score', 0),
                'avg_question_length': adv_report.get('avg_question_length', 0)
            })
        except Exception as e:
            print(f"⚠️ Error processing {name}: {e}")

    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(summary_path, index=False)
        print(f"\n📄 Summary saved to: {summary_path}")
        print(summary_df)

if __name__ == '__main__':
    main()
