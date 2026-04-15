#!/usr/bin/env python3
"""
Calibration Metrics for AGI Hackathon Evaluation
Implements Expected Calibration Error (ECE) and Brier Score
following best practices from Guo et al. (2017) and Jiang et al. (2021).

Author: AGI Hackathon Team
Date: 2026-04-15

References:
- Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017).
  On calibration of modern neural networks.
- Jiang, L., Bansal, N., & Madani, O. (2021).
  Conformal Prediction for Reliable Uncertainty Quantification.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class CalibrationResult:
    """Result of calibration analysis"""
    ece: float  # Expected Calibration Error
    brier_score: float  # Brier Score
    reliability: Dict[str, Dict]  # Per-bin reliability data
    over_confidence: float  # Average over-confidence
    under_confidence: float  # Average under-confidence


def compute_ece(
    confidences: np.ndarray,
    correct: np.ndarray,
    n_bins: int = 10
) -> float:
    """
    Compute Expected Calibration Error (ECE).

    ECE = Σ(b=1 to B) |Nb / N| * |acc(b) - conf(b)|

    Where:
    - B = number of bins
    - Nb = number of predictions in bin b
    - N = total number of predictions
    - acc(b) = accuracy in bin b
    - conf(b) = average confidence in bin b

    Args:
        confidences: Array of confidence values (0-100)
        correct: Array of correctness (0/1)
        n_bins: Number of bins (default: 10, standard in literature)

    Returns:
        ECE value (lower is better, 0 = perfectly calibrated)
    """
    # Normalize confidences to [0, 1]
    conf_norm = confidences / 100.0

    # Create bins
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]

    ece = 0.0
    total_samples = len(confidences)

    for lower, upper in zip(bin_lowers, bin_uppers):
        # Find predictions in this bin
        in_bin = (conf_norm > lower) & (conf_norm <= upper)
        n_in_bin = in_bin.sum()

        if n_in_bin == 0:
            continue

        # Accuracy in this bin
        correct_in_bin = correct[in_bin]
        acc_in_bin = correct_in_bin.mean()

        # Average confidence in this bin
        conf_in_bin = conf_norm[in_bin].mean()

        # Weighted contribution to ECE
        ece += (n_in_bin / total_samples) * abs(acc_in_bin - conf_in_bin)

    return ece


def compute_brier_score(
    confidences: np.ndarray,
    correct: np.ndarray,
    n_classes: int = 4
) -> float:
    """
    Compute Brier Score for multi-class calibration.

    BS = (1/N) * Σ(i=1 to N) Σ(k=1 to K) (f_k - y_k)^2

    Where:
    - f_k = predicted probability for class k
    - y_k = one-hot encoded true label
    - K = number of classes (4 for A/B/C/D)

    Args:
        confidences: Array of confidence values (0-100)
        correct: Array of correctness (0/1)
        n_classes: Number of classes (default: 4 for A/B/C/D)

    Returns:
        Brier Score (lower is better, 0 = perfect)
    """
    # Normalize confidences to [0, 1]
    probs = confidences / 100.0

    # For multi-class, we need full probability distributions
    # Since we only have confidence for one class, we approximate:
    # - Selected class gets confidence probability
    # - Remaining probability is distributed among other classes

    N = len(confidences)
    brier = 0.0

    for i in range(N):
        # One-hot encode correct answer
        # For incorrect answers, we need to know which class was predicted
        # This is a simplified version assuming binary case (correct/incorrect)
        y = 1.0 if correct[i] else 0.0

        # Predicted probability for correct answer
        f = probs[i] if correct[i] else (1 - probs[i]) / (n_classes - 1)

        # Brier score contribution
        brier += (f - y) ** 2

    return brier / N


def compute_adaptive_ece(
    confidences: np.ndarray,
    correct: np.ndarray,
    n_bins: int = 15
) -> float:
    """
    Compute Adaptive ECE with bins adjusted for sample distribution.
    Uses quantile-based binning for more robust estimates.

    Args:
        confidences: Array of confidence values (0-100)
        correct: Array of correctness (0/1)
        n_bins: Number of bins (default: 15 for adaptive)

    Returns:
        Adaptive ECE value
    """
    # Normalize confidences to [0, 1]
    conf_norm = confidences / 100.0

    # Create quantile-based bins
    quantiles = np.linspace(0, 1, n_bins + 1)
    bin_boundaries = np.quantile(conf_norm, quantiles)
    bin_boundaries[0] = 0.0  # Ensure boundaries cover full range
    bin_boundaries[-1] = 1.0

    # Remove duplicate boundaries
    bin_boundaries = np.unique(bin_boundaries)

    ece = 0.0
    total_samples = len(confidences)

    for i in range(len(bin_boundaries) - 1):
        lower = bin_boundaries[i]
        upper = bin_boundaries[i + 1]

        # Find predictions in this bin
        in_bin = (conf_norm >= lower) & (conf_norm <= upper)
        n_in_bin = in_bin.sum()

        if n_in_bin == 0:
            continue

        correct_in_bin = correct[in_bin]
        acc_in_bin = correct_in_bin.mean()
        conf_in_bin = conf_norm[in_bin].mean()

        ece += (n_in_bin / total_samples) * abs(acc_in_bin - conf_in_bin)

    return ece


def compute_reliability_diagram(
    confidences: np.ndarray,
    correct: np.ndarray,
    n_bins: int = 10
) -> Dict[str, Dict]:
    """
    Compute data for reliability diagram.

    Args:
        confidences: Array of confidence values (0-100)
        correct: Array of correctness (0/1)
        n_bins: Number of bins

    Returns:
        Dictionary with bin data for plotting
    """
    # Normalize confidences to [0, 1]
    conf_norm = confidences / 100.0

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]

    reliability = {}

    for i, (lower, upper) in enumerate(zip(bin_lowers, bin_uppers)):
        in_bin = (conf_norm > lower) & (conf_norm <= upper)
        n_in_bin = in_bin.sum()

        if n_in_bin == 0:
            continue

        correct_in_bin = correct[in_bin]
        acc_in_bin = correct_in_bin.mean()
        conf_in_bin = conf_norm[in_bin].mean()

        # Calculate standard error for error bars
        se_in_bin = np.sqrt(acc_in_bin * (1 - acc_in_bin) / n_in_bin)

        bin_name = f"{int(lower*100)}-{int(upper*100)}%"
        reliability[bin_name] = {
            'confidence_mid': (lower + upper) / 2,
            'accuracy': acc_in_bin,
            'avg_confidence': conf_in_bin,
            'count': n_in_bin,
            'std_error': se_in_bin,
            'calibration_error': abs(acc_in_bin - conf_in_bin)
        }

    return reliability


def compute_over_under_confidence(
    confidences: np.ndarray,
    correct: np.ndarray
) -> Tuple[float, float]:
    """
    Compute average over-confidence and under-confidence.

    Args:
        confidences: Array of confidence values (0-100)
        correct: Array of correctness (0/1)

    Returns:
        Tuple of (over_confidence, under_confidence)
    """
    # Normalize confidences to [0, 1]
    conf_norm = confidences / 100.0

    # Over-confidence: high confidence on wrong answers
    over_conf = conf_norm[~correct.astype(bool)].mean() if (~correct).sum() > 0 else 0.0

    # Under-confidence: low confidence on correct answers
    under_conf = (1 - conf_norm[correct.astype(bool)]).mean() if correct.sum() > 0 else 0.0

    return over_conf, under_conf


def full_calibration_analysis(
    confidences: List[float],
    correct: List[bool],
    n_bins: int = 10
) -> CalibrationResult:
    """
    Perform full calibration analysis.

    Args:
        confidences: List of confidence values (0-100)
        correct: List of correctness (True/False)
        n_bins: Number of bins for ECE

    Returns:
        CalibrationResult with all metrics
    """
    # Convert to numpy arrays
    conf_array = np.array(confidences)
    correct_array = np.array(correct, dtype=int)

    # Compute metrics
    ece = compute_ece(conf_array, correct_array, n_bins)
    adaptive_ece = compute_adaptive_ece(conf_array, correct_array, n_bins + 5)
    brier = compute_brier_score(conf_array, correct_array)
    reliability = compute_reliability_diagram(conf_array, correct_array, n_bins)
    over_conf, under_conf = compute_over_under_confidence(conf_array, correct_array)

    return CalibrationResult(
        ece=ece,
        brier_score=brier,
        reliability=reliability,
        over_confidence=over_conf,
        under_confidence=under_conf
    )


def format_calibration_summary(result: CalibrationResult) -> str:
    """Format calibration result as readable string"""
    lines = [
        "📊 Calibration Analysis",
        "=" * 50,
        f"Expected Calibration Error (ECE): {result.ece:.4f}",
        f"  (< 0.05 = excellent, < 0.10 = good, < 0.15 = fair)",
        f"",
        f"Brier Score: {result.brier_score:.4f}",
        f"  (lower is better, 0 = perfect)",
        f"",
        f"Over-confidence: {result.over_confidence:.2%}",
        f"Under-confidence: {result.under_confidence:.2%}",
        f"",
        f"Per-bin reliability:",
    ]

    for bin_name, data in result.reliability.items():
        cal_error = data['calibration_error']
        status = "✅" if cal_error < 0.10 else "⚠️" if cal_error < 0.20 else "❌"
        lines.append(
            f"  {bin_name:>6}: acc={data['accuracy']:.2%}, "
            f"conf={data['avg_confidence']:.2%}, "
            f"n={data['count']} {status}"
        )

    return "\n".join(lines)


def test_calibration_metrics():
    """Test calibration metrics with synthetic data"""

    print("Testing Calibration Metrics")
    print("=" * 60)

    # Perfectly calibrated model
    print("\n1. Perfectly Calibrated Model")
    conf_perfect = np.array([50, 60, 70, 80, 90])
    correct_perfect = np.array([0, 0, 1, 1, 1])  # 50/50, 60/40, 70/30, 80/20, 90/10 split
    result = full_calibration_analysis(conf_perfect.tolist(), correct_perfect.tolist())
    print(format_calibration_summary(result))

    # Over-confident model
    print("\n2. Over-confident Model (high confidence, low accuracy)")
    conf_over = np.array([90, 90, 90, 90, 90])
    correct_over = np.array([0, 0, 0, 1, 1])
    result = full_calibration_analysis(conf_over.tolist(), correct_over.tolist())
    print(format_calibration_summary(result))

    # Under-confident model
    print("\n3. Under-confident Model (low confidence, high accuracy)")
    conf_under = np.array([50, 50, 50, 50, 50])
    correct_under = np.array([1, 1, 1, 1, 1])
    result = full_calibration_analysis(conf_under.tolist(), correct_under.tolist())
    print(format_calibration_summary(result))


if __name__ == "__main__":
    test_calibration_metrics()
