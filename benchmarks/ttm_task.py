"""
TTM (Trinity Metacognitive) Physics-Enhanced Task

This task evaluates metacognitive calibration using physics-enhanced questions
that reveal whether models can detect errors and adjust strategies.

Adversarial dataset: playra/trinity-ttm-physics-enhanced (199 questions)
Expected accuracy: 10-25% (vs 100% on artificial dataset)
"""

import kaggle_benchmarks as kbench
import pandas as pd
from dataclasses import dataclass

# Load physics-enhanced TTM dataset
DATASET_PATH = "/kaggle/input/playra/trinity-ttm-physics-enhanced/ttm_physics_mc.csv"


@dataclass
class MCAnswer:
    """Schema for multiple choice answers."""
    answer: str


@kbench.task(name="ttm_physics_mc", store_task=False)
def ttm_physics_mc(llm, question: str, a: str, b: str, c: str, d: str, expected: str) -> bool:
    """Single TTM physics-enhanced multiple choice question."""
    response = llm.prompt(f"Question: {question}\nA: {a}\nB: {b}\nC: {c}\nD: {d}\nAnswer (A/B/C/D):", schema=MCAnswer)
    got = response.answer.strip().upper()[:1]
    exp = expected.strip().upper()
    llm.logger.info(f"TTM | Got: {got} | Exp: {exp} | {'✓' if got==exp else '✗'}")
    return got == exp


@kbench.task(name="ttm_benchmark", description="TTM Physics-Enhanced Metacognition")
def ttm_benchmark(llm):
    """Main TTM benchmark function."""
    try:
        df = pd.read_csv(DATASET_PATH)
    except FileNotFoundError:
        print("[TTM] Dataset not found, skipping")
        return

    print(f"[TTM] Loaded {len(df)} physics-enhanced questions")

    with kbench.client.enable_cache():
        runs = ttm_physics_mc.evaluate(llm=[llm], evaluation_data=df, n_jobs=2, timeout=180)

    results_df = runs.as_dataframe()
    valid = results_df[results_df['result'].notna()]
    accuracy = float(valid['result'].mean()) if len(valid) > 0 else 0

    print(f"TTM: {accuracy:.1%} ({int(valid['result'].sum())}/{len(valid)})")

    kbench.assertions.assert_true(accuracy > 0, expectation=f"TTM: {accuracy:.1%}")
    return {"accuracy": accuracy, "total": len(valid)}
