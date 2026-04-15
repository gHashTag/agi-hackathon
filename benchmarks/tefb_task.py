"""
TEFB (Trinity Executive Function Battery) Cleaned Task

This task evaluates executive functions: planning, working memory,
cognitive flexibility, and inhibition control.

Cleaned dataset: playra/trinity-tefb-cleaned (1,512 questions)
Expected accuracy: 50-70%
"""

import kaggle_benchmarks as kbench
import pandas as pd
from dataclasses import dataclass

# Load cleaned TEFB dataset
DATASET_PATH = "/kaggle/input/playra/trinity-tefb-cleaned/tefb_mc_cleaned.csv"


@dataclass
class MCAnswer:
    """Schema for multiple choice answers."""
    answer: str


@kbench.task(name="tefb_cleaned_mc", store_task=False)
def tefb_cleaned_mc(llm, question: str, a: str, b: str, c: str, d: str, expected: str) -> bool:
    """Single TEFB cleaned multiple choice question."""
    response = llm.prompt(f"Question: {question}\nA: {a}\nB: {b}\nC: {c}\nD: {d}\nAnswer (A/B/C/D):", schema=MCAnswer)
    got = response.answer.strip().upper()[:1]
    exp = expected.strip().upper()
    llm.logger.info(f"TEFB | Got: {got} | Exp: {exp} | {'✓' if got==exp else '✗'}")
    return got == exp


@kbench.task(name="tefb_benchmark", description="TEFB Cleaned Executive Function")
def tefb_benchmark(llm):
    """Main TEFB benchmark function."""
    try:
        df = pd.read_csv(DATASET_PATH)
    except FileNotFoundError:
        print("[TEFB] Dataset not found, skipping")
        return

    print(f"[TEFB] Loaded {len(df)} cleaned questions")

    with kbench.client.enable_cache():
        runs = tefb_cleaned_mc.evaluate(llm=[llm], evaluation_data=df, n_jobs=2, timeout=180)

    results_df = runs.as_dataframe()
    valid = results_df[results_df['result'].notna()]
    accuracy = float(valid['result'].mean()) if len(valid) > 0 else 0

    print(f"TEFB: {accuracy:.1%} ({int(valid['result'].sum())}/{len(valid)})")

    kbench.assertions.assert_true(accuracy > 0, expectation=f"TEFB: {accuracy:.1%}")
    return {"accuracy": accuracy, "total": len(valid)}
