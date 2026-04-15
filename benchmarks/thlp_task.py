"""
THLP (Trinity Hierarchical Learning Pattern) Adversarial Task

This task evaluates whether LLMs can truly learn patterns from examples
rather than relying on memorization.

Adversarial dataset: playra/trinity-thlp-adversarial (274 questions)
Expected accuracy: 25-40% (vs 80%+ on standard dataset)
"""

import kaggle_benchmarks as kbench
import pandas as pd
from dataclasses import dataclass

# Load adversarial THLP dataset
DATASET_PATH = "/kaggle/input/playra/trinity-thlp-adversarial/thlp_mc_aggressive.csv"


@dataclass
class MCAnswer:
    """Schema for multiple choice answers."""
    answer: str


@kbench.task(name="thlp_adversarial_mc", store_task=False)
def thlp_adversarial_mc(llm, question: str, a: str, b: str, c: str, d: str, expected: str) -> bool:
    """Single THLP adversarial multiple choice question."""
    response = llm.prompt(f"Question: {question}\nA: {a}\nB: {b}\nC: {c}\nD: {d}\nAnswer (A/B/C/D):", schema=MCAnswer)
    got = response.answer.strip().upper()[:1]
    exp = expected.strip().upper()
    llm.logger.info(f"THLP | Got: {got} | Exp: {exp} | {'✓' if got==exp else '✗'}")
    return got == exp


@kbench.task(name="thlp_benchmark", description="THLP Adversarial Pattern Learning")
def thlp_benchmark(llm):
    """Main THLP benchmark function."""
    try:
        df = pd.read_csv(DATASET_PATH)
    except FileNotFoundError:
        print("[THLP] Dataset not found, skipping")
        return

    print(f"[THLP] Loaded {len(df)} questions from adversarial dataset")

    with kbench.client.enable_cache():
        runs = thlp_adversarial_mc.evaluate(llm=[llm], evaluation_data=df, n_jobs=2, timeout=180)

    results_df = runs.as_dataframe()
    valid = results_df[results_df['result'].notna()]
    accuracy = float(valid['result'].mean()) if len(valid) > 0 else 0

    print(f"THLP: {accuracy:.1%} ({int(valid['result'].sum())}/{len(valid)})")

    kbench.assertions.assert_true(accuracy > 0, expectation=f"THLP: {accuracy:.1%}")
    return {"accuracy": accuracy, "total": len(valid)}
