"""
TSCP (Trinity Social Cognition Protocol) Cleaned Task

This task evaluates theory of mind, pragmatic inference,
and social reasoning capabilities.

Cleaned dataset: playra/trinity-tscp-cleaned (25 questions)
Expected accuracy: 60-80%
"""

import kaggle_benchmarks as kbench
import pandas as pd
from dataclasses import dataclass

# Load cleaned TSCP dataset
DATASET_PATH = "/kaggle/input/playra/trinity-tscp-cleaned/tscp_mc_cleaned.csv"


@dataclass
class MCAnswer:
    """Schema for multiple choice answers."""
    answer: str


@kbench.task(name="tscp_cleaned_mc", store_task=False)
def tscp_cleaned_mc(llm, question: str, a: str, b: str, c: str, d: str, expected: str) -> bool:
    """Single TSCP cleaned multiple choice question."""
    response = llm.prompt(f"Question: {question}\nA: {a}\nB: {b}\nC: {c}\nD: {d}\nAnswer (A/B/C/D):", schema=MCAnswer)
    got = response.answer.strip().upper()[:1]
    exp = expected.strip().upper()
    llm.logger.info(f"TSCP | Got: {got} | Exp: {exp} | {'✓' if got==exp else '✗'}")
    return got == exp


@kbench.task(name="tscp_benchmark", description="TSCP Cleaned Social Cognition")
def tscp_benchmark(llm):
    """Main TSCP benchmark function."""
    try:
        df = pd.read_csv(DATASET_PATH)
    except FileNotFoundError:
        print("[TSCP] Dataset not found, skipping")
        return

    print(f"[TSCP] Loaded {len(df)} cleaned questions")

    with kbench.client.enable_cache():
        runs = tscp_cleaned_mc.evaluate(llm=[llm], evaluation_data=df, n_jobs=2, timeout=180)

    results_df = runs.as_dataframe()
    valid = results_df[results_df['result'].notna()]
    accuracy = float(valid['result'].mean()) if len(valid) > 0 else 0

    print(f"TSCP: {accuracy:.1%} ({int(valid['result'].sum())}/{len(valid)})")

    kbench.assertions.assert_true(accuracy > 0, expectation=f"TSCP: {accuracy:.1%}")
    return {"accuracy": accuracy, "total": len(valid)}
