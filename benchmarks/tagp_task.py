"""
TAGP (Trinity Attention Grid Pattern) Adversarial Task

This task evaluates attention control - selective focus, sustained attention,
and resistance to distraction.

Adversarial dataset: playra/trinity-tagp-adversarial (851 questions)
Expected accuracy: 20-35% (vs 100% on standard dataset)
"""

import kaggle_benchmarks as kbench
import pandas as pd
from dataclasses import dataclass

# Load adversarial TAGP dataset
DATASET_PATH = "/kaggle/input/playra/trinity-tagp-adversarial/tagp_mc_aggressive.csv"


@dataclass
class MCAnswer:
    """Schema for multiple choice answers."""
    answer: str


@kbench.task(name="tagp_adversarial_mc", store_task=False)
def tagp_adversarial_mc(llm, question: str, a: str, b: str, c: str, d: str, expected: str) -> bool:
    """Single TAGP adversarial multiple choice question."""
    response = llm.prompt(f"Question: {question}\nA: {a}\nB: {b}\nC: {c}\nD: {d}\nAnswer (A/B/C/D):", schema=MCAnswer)
    got = response.answer.strip().upper()[:1]
    exp = expected.strip().upper()
    llm.logger.info(f"TAGP | Got: {got} | Exp: {exp} | {'✓' if got==exp else '✗'}")
    return got == exp


@kbench.task(name="tagp_benchmark", description="TAGP Adversarial Attention Control")
def tagp_benchmark(llm):
    """Main TAGP benchmark function."""
    try:
        df = pd.read_csv(DATASET_PATH)
    except FileNotFoundError:
        print("[TAGP] Dataset not found, skipping")
        return

    print(f"[TAGP] Loaded {len(df)} adversarial questions")

    with kbench.client.enable_cache():
        runs = tagp_adversarial_mc.evaluate(llm=[llm], evaluation_data=df, n_jobs=2, timeout=180)

    results_df = runs.as_dataframe()
    valid = results_df[results_df['result'].notna()]
    accuracy = float(valid['result'].mean()) if len(valid) > 0 else 0

    print(f"TAGP: {accuracy:.1%} ({int(valid['result'].sum())}/{len(valid)})")

    kbench.assertions.assert_true(accuracy > 0, expectation=f"TAGP: {accuracy:.1%}")
    return {"accuracy": accuracy, "total": len(valid)}
