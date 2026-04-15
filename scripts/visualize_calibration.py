#!/usr/bin/env python3
"""
Calibration Visualization Module for AGI Hackathon
Creates reliability diagrams, calibration curves, and summary statistics.

Author: AGI Hackathon Team
Date: 2026-04-15

References:
- Niculescu-Mizil & Caruana (2005) - Predicting Good Probabilities
- Guo et al. (2017) - On calibration of modern neural networks
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple
import calibration_metrics


def load_results(result_file: Path) -> Dict:
    """Load evaluation results from JSON"""
    with open(result_file, 'r') as f:
        return json.load(f)


def plot_reliability_diagram(
    confidences: np.ndarray,
    correct: np.ndarray,
    model_name: str,
    track: str = "",
    output_dir: Path = Path('runs')
) -> Path:
    """
    Create reliability diagram showing calibration across confidence bins.

    Args:
        confidences: Array of confidence values (0-100)
        correct: Array of correctness
        model_name: Name of the model
        track: Cognitive track name
        output_dir: Directory to save plots

    Returns:
        Path to saved plot
    """
    # Compute reliability data
    reliability = calibration_metrics.compute_reliability_diagram(confidences, correct)

    # Extract data for plotting
    bins = list(reliability.keys())
    conf_mids = [reliability[b]['confidence_mid'] for b in bins]
    accuracies = [reliability[b]['accuracy'] for b in bins]
    counts = [reliability[b]['count'] for b in bins]
    errors = [reliability[b]['std_error'] for b in bins]

    # Filter empty bins
    valid_bins = [b for b, c in zip(bins, counts) if c > 0]
    conf_mids = [reliability[b]['confidence_mid'] for b in valid_bins]
    accuracies = [reliability[b]['accuracy'] for b in valid_bins]
    counts = [reliability[b]['count'] for b in valid_bins]
    errors = [reliability[b]['std_error'] for b in valid_bins]

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 7))

    # Plot calibration curve
    ax.plot(conf_mids, accuracies, 'o-', linewidth=2, label='Model Calibration', markersize=8)
    ax.plot(conf_mids, conf_mids, '--', linewidth=1, color='gray', alpha=0.7, label='Perfect Calibration')

    # Fill between for visual clarity
    ax.fill_between(conf_mids, 0, accuracies, alpha=0.3, color='green')
    ax.fill_between(conf_mids, accuracies, conf_mids, alpha=0.3, color='orange')

    # Add error bars
    ax.errorbar(conf_mids, accuracies, yerr=errors, fmt='o', capsize=3, alpha=0.6)

    # Add count labels
    for i, (cmid, acc, count) in enumerate(zip(conf_mids, accuracies, counts)):
        ax.text(cmid, acc - 0.08, f'n={count}', fontsize=8, ha='center')

    # Perfect calibration line
    ax.plot([0, 100], [0, 100], '--', linewidth=1, color='gray', alpha=0.7)

    # Formatting
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel('Confidence (%)', fontsize=12)
    ax.set_ylabel('Actual Accuracy (%)', fontsize=12)
    ax.set_title(f'Reliability Diagram: {model_name.upper()}{f" - {track}" if track else ""}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right', fontsize=10)

    plt.tight_layout()

    # Save plot
    output_file = output_dir / f"{model_name}_reliability{f'_{track}' if track else ''}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  📊 Saved reliability diagram: {output_file}")
    return output_file


def plot_calibration_comparison(
    results: Dict[str, Dict],
    track: str = "",
    output_dir: Path = Path('runs')
) -> Path:
    """
    Compare calibration across multiple models.

    Args:
        results: Dictionary of model -> result data
        track: Cognitive track name
        output_dir: Directory to save plots

    Returns:
        Path to saved plot
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot each model
    colors = ['#1f77b4', '#ff7f0e', '#2ecc71', '#e74c3c']
    markers = ['o', 's', '^', 'D']

    for i, (model, data) in enumerate(results.items()):
        if 'summary' not in data or 'calibration' not in data['summary']:
            continue

        cal = data['summary']['calibration']
        if 'basic' not in cal:
            continue

        # Extract bin data
        bins = list(cal['basic'].keys())
        accuracies = [cal['basic'][b]['accuracy'] * 100 for b in bins]
        counts = [cal['basic'][b]['count'] for b in bins]

        # Filter valid bins
        valid_bins = [b for b, c in zip(bins, counts) if c > 0]
        if len(valid_bins) < 2:
            continue

        bin_mids = [(int(b.split('-')[0]) + int(b.split('-')[1].rstrip('%'))) / 2
                        for b in valid_bins]
        valid_acc = [cal['basic'][b]['accuracy'] * 100 for b in valid_bins]

        ax.plot(bin_mids, valid_acc, marker=markers[i % len(markers)],
                linewidth=2, label=model.upper(), color=colors[i % len(colors)], markersize=8)

    # Perfect calibration line
    ax.plot([0, 100], [0, 100], '--', linewidth=1, color='gray', alpha=0.5, label='Perfect')

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel('Confidence Bin Midpoint (%)', fontsize=12)
    ax.set_ylabel('Actual Accuracy (%)', fontsize=12)
    track_title = f" - {track}" if track else ""
    ax.set_title(f'Calibration Comparison{track_title}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right', fontsize=10)

    plt.tight_layout()

    output_file = output_dir / f"calibration_comparison{track_title.replace(' ', '_')}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  📊 Saved calibration comparison: {output_file}")
    return output_file


def plot_over_under_confidence(
    results: Dict[str, Dict],
    output_dir: Path = Path('runs')
) -> Path:
    """
    Plot over-confidence and under-confidence across models.

    Args:
        results: Dictionary of model -> result data
        output_dir: Directory to save plots

    Returns:
        Path to saved plot
    """
    models = []
    over_conf = []
    under_conf = []

    for model, data in results.items():
        if 'summary' not in data or 'calibration' not in data['summary']:
            continue

        cal = data['summary']['calibration']
        over_conf.append(cal.get('over_confidence', 0) * 100)
        under_conf.append(cal.get('under_confidence', 0) * 100)
        models.append(model.upper())

    if not models:
        return None

    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(models))
    width = 0.35

    bars1 = ax.bar(x - width/2, over_conf, width, label='Over-Confidence', color='#e74c3c', alpha=0.8)
    bars2 = ax.bar(x + width/2, under_conf, width, label='Under-Confidence', color='#1f77b4', alpha=0.8)

    ax.set_ylabel('Percentage (%)', fontsize=12)
    ax.set_title('Confidence Bias Across Models', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend(loc='upper right', fontsize=10)
    ax.set_ylim(0, 100)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for i in range(len(models)):
        ax.text(i - width/2, over_conf[i] + 1, f'{over_conf[i]:.1f}', ha='center', va='bottom', fontsize=9)
        ax.text(i + width/2, under_conf[i] + 1, f'{under_conf[i]:.1f}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()

    output_file = output_dir / "confidence_bias.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  📊 Saved confidence bias plot: {output_file}")
    return output_file


def create_calibration_report(
    results: Dict[str, Dict],
    output_dir: Path = Path('runs')
) -> Path:
    """
    Create comprehensive calibration report.

    Args:
        results: Dictionary of model -> result data
        output_dir: Directory to save report

    Returns:
        Path to saved report
    """
    lines = [
        "# Calibration Analysis Report",
        f"\n**Generated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Summary Statistics",
        ""
    ]

    for model, data in results.items():
        if 'summary' not in data or 'calibration' not in data['summary']:
            continue

        cal = data['summary']['calibration']
        lines.extend([
            f"### {model.upper()}",
            f"",
        ])

        if 'ece' in cal:
            lines.append(f"- **Expected Calibration Error (ECE):** {cal['ece']:.4f}")
            ece_level = "✅ Excellent" if cal['ece'] < 0.05 else "✓ Good" if cal['ece'] < 0.10 else "⚠️ Fair" if cal['ece'] < 0.15 else "❌ Poor"
            lines.append(f"  Level: {ece_level}")
            lines.append("")

        if 'brier_score' in cal:
            lines.append(f"- **Brier Score:** {cal['brier_score']:.4f}")
            lines.append(f"  (lower is better, 0 = perfect)")
            lines.append("")

        if 'over_confidence' in cal and 'under_confidence' in cal:
            lines.extend([
                f"- **Over-Confidence:** {cal['over_confidence'] * 100:.2f}%",
                f"- **Under-Confidence:** {cal['under_confidence'] * 100:.2f}%",
                ""
            ])

    # Save report
    output_file = output_dir / "calibration_report.md"
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))

    print(f"  📊 Saved calibration report: {output_file}")
    return output_file


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Calibration visualization module")
    parser.add_argument('--result-file', type=str, default=None,
                       help='Single result file to visualize')
    parser.add_argument('--result-dir', type=str, default=None,
                       help='Directory containing result files')
    parser.add_argument('--track', type=str, default=None,
                       help='Filter by track name')
    parser.add_argument('--output-dir', type=str, default='runs',
                       help='Output directory for plots')

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    # Load results
    if args.result_file:
        result_path = Path(args.result_file)
        if result_path.exists():
            model = result_path.stem.split('_')[0]
            results[model] = load_results(result_path)
    elif args.result_dir:
        result_dir = Path(args.result_dir)
        for result_file in result_dir.glob('*_results.json'):
            if 'final' in result_file.name.lower():
                continue

            model = result_file.stem.split('_')[0]
            results[model] = load_results(result_file)

    if not results:
        print("No results found!")
        return

    # Generate plots
    track_filter = args.track.lower() if args.track else ""

    for model, data in results.items():
        if 'summary' not in data or 'results' not in data:
            continue

        confidences = np.array([r['confidence'] for r in data['results']])
        correct = np.array([1 if r.get('correct') else 0 for r in data['results']])

        if len(confidences) > 0:
            plot_reliability_diagram(
                confidences, correct,
                model=model,
                track=track_filter,
                output_dir=output_dir
            )

    # Compare models
    plot_calibration_comparison(results, track=track_filter, output_dir=output_dir)
    plot_over_under_confidence(results, output_dir=output_dir)
    create_calibration_report(results, output_dir=output_dir)

    print("\n✅ Calibration visualization complete!")


if __name__ == "__main__":
    main()
