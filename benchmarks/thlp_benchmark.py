"""
THLP (Trinity Hierarchical Learning Pattern) Adversarial Benchmark

This benchmark tests whether LLMs can truly learn patterns from examples
rather than relying on memorization.

Adversarial dataset includes 274 questions designed to break memorization:
- Pattern-breaking questions
- Negative constraints
- Paraphrased versions
- Complex reasoning requirements

Expected model accuracy: 25-40% (vs 80%+ on standard dataset)
"""

import kaggle_benchmarks as kbench
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Any

# Load adversarial THLP dataset
THLP_DATASET_URL = "playra/trinity-thlp-adversarial"
THLP_DATASET_PATH = f"/kaggle/input/{THLP_DATASET_URL}/thlp_mc_aggressive.csv"


@dataclass
class MCAnswer:
    """Schema for multiple choice answers."""
    answer: str


def load_thlp_data() -> pd.DataFrame:
    """Load and prepare THLP adversarial dataset."""
    try:
        # Try Kaggle path first
        df = pd.read_csv(THLP_DATASET_PATH)
        print(f"[THLP] Loaded {len(df)} questions from adversarial dataset")
    except FileNotFoundError:
        print(f"[THLP] Kaggle dataset not found, skipping benchmark")
        return None

    # Validate and prepare data
    required_cols = ['question', 'A', 'B', 'C', 'D', 'answer']
    for col in required_cols:
        if col not in df.columns:
            print(f"[THLP] Missing column: {col}")
            return None

    # Clean answers
    df['expected_answer'] = df['answer'].astype(str).str.strip().str.upper()

    # Validate answer format
    invalid_mask = ~df['expected_answer'].str.match(r'^[A-D]$')
    if invalid_mask.any():
        print(f"[THLP] Warning: {invalid_mask.sum()} invalid answers")

    # Calculate answer distribution
    dist = df['expected_answer'].value_counts(normalize=True).sort_index()
    print(f"[THLP] Answer distribution: {dict(dist.round(3))}")

    return df


@kbench.task(name="thlp_adversarial_mc", store_task=False)
def thlp_adversarial_mc(
    llm,
    question: str,
    choice_a: str,
    choice_b: str,
    choice_c: str,
    choice_d: str,
    expected_answer: str
) -> bool:
    """
    Single THLP adversarial multiple choice question.

    Args:
        llm: The language model to evaluate
        question: The question text
        choice_a/b/c/d: The four answer choices
        expected_answer: The correct answer (A, B, C, or D)

    Returns:
        True if the model's answer matches the expected answer
    """
    # Build prompt with adversarial warnings
    prompt = f"""Answer the following multiple choice question with ONLY ONE letter (A, B, C, or D).
Do not explain. Return exactly one character.

Question: {question}

Choices:
A: {choice_a}
B: {choice_b}
C: {choice_c}
D: {choice_d}

Your answer (A/B/C/D):"""

    # Get model response
    response = llm.prompt(prompt, schema=MCAnswer)
    got = response.answer.strip().upper()[:1]
    exp = expected_answer.strip().upper()

    # Validate
    is_correct = (got == exp)

    # Log result for analysis
    llm.logger.info(f"THLP_Adversarial | Q: {question[:50]}... | Got: {got} | Expected: {exp} | Correct: {is_correct}")

    return is_correct


@kbench.task(name="thlp_benchmark", description="THLP Adversarial Pattern Learning Benchmark")
def thlp_benchmark(llm) -> Dict[str, Any]:
    """
    Main THLP benchmark function.

    Evaluates the model on all adversarial THLP questions
    and returns detailed metrics.

    Args:
        llm: The language model to evaluate

    Returns:
        Dictionary with benchmark metrics
    """
    # Load dataset
    df = load_thlp_data()
    if df is None or len(df) == 0:
        return {"error": "Failed to load dataset"}

    print(f"[THLP] Starting benchmark with {len(df)} questions...")

    # Run evaluation
    with kbench.client.enable_cache():
        runs = thlp_adversarial_mc.evaluate(
            llm=[llm],
            evaluation_data=df,
            n_jobs=2,          # Parallel execution
            timeout=180,        # 3 minutes per question
            max_attempts=2,
            remove_run_files=True
        )

    # Calculate metrics
    results_df = runs.as_dataframe()
    valid_results = results_df[results_df['result'].notna()]

    total = len(valid_results)
    correct = int(valid_results['result'].sum())
    accuracy = float(valid_results['result'].mean()) if total > 0 else 0.0

    # Per-class accuracy
    class_accuracy = {}
    for answer in ['A', 'B', 'C', 'D']:
        subset = results_df[results_df['expected_answer'] == answer]
        subset_valid = subset[subset['result'].notna()]
        if len(subset_valid) > 0:
            class_accuracy[answer] = {
                'total': len(subset_valid),
                'correct': int(subset_valid['result'].sum()),
                'accuracy': float(subset_valid['result'].mean())
            }

    # Expected vs Actual
    expected_range = [25, 40]  # 25-40% for adversarial
    in_range = expected_range[0] <= accuracy * 100 <= expected_range[1]

    # Results summary
    metrics = {
        "total_questions": total,
        "correct_answers": correct,
        "accuracy": accuracy,
        "accuracy_percent": accuracy * 100,
        "class_accuracy": class_accuracy,
        "in_expected_range": in_range,
        "expected_range": f"{expected_range[0]}-{expected_range[1]}%",
        "sample_size": "Adversarial (274 questions)",
        "adversarial_features": [
            "Pattern-breaking questions",
            "Negative constraints",
            "Paraphrased versions",
            "Complex reasoning"
        ]
    }

    print(f"\n[THLP] Results:")
    print(f"  Accuracy: {accuracy:.2%} ({correct}/{total})")
    print(f"  Expected: {expected_range[0]}-{expected_range[1]}%")
    print(f"  In range: {'YES ✓' if in_range else 'NO ✗'}")

    # Assertions for leaderboard
    kbench.assertions.assert_true(
        accuracy > 0,
        expectation=f"THLP Adversarial accuracy: {accuracy:.2%} ({correct}/{total})"
    )

    kbench.assertions.assert_true(
        in_range,
        expectation=f"Accuracy {accuracy:.1%} falls within expected adversarial range"
    )

    return metrics


# Run benchmark when executed
if __name__ == "__main__":
    # This will be executed by Kaggle Benchmarks
    run = thlp_benchmark.run(kbench.llm)
    print(f"\n[THLP] Benchmark complete!")
