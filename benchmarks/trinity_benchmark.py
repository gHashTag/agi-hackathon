"""
AGI Hackathon 2026 - Trinity Cognitive Probes Adversarial Benchmarks

This package contains 5 adversarial benchmarks testing true cognitive capabilities
rather than memorization.

Adversarial datasets include pattern-breaking questions designed to reveal
whether models truly possess the targeted cognitive abilities.

Total: 2,861 questions across 5 cognitive tracks
"""

import kaggle_benchmarks as kbench
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Any

# Dataset URLs and paths
DATASETS = {
    "thlp": {
        "name": "THLP",
        "title": "Trinity Hierarchical Learning Pattern",
        "kaggle": "playra/trinity-thlp-adversarial",
        "file": "thlp_mc_aggressive.csv",
        "questions": 274,
        "expected_range": [25, 40],  # 25-40% for adversarial
        "features": ["Pattern-breaking", "Negative constraints", "Paraphrased"]
    },
    "ttm": {
        "name": "TTM",
        "title": "Trinity Metacognitive",
        "kaggle": "playra/trinity-ttm-physics-enhanced",
        "file": "ttm_physics_mc.csv",
        "questions": 199,
        "expected_range": [10, 25],  # 10-25% for physics enhanced
        "features": ["Physics domain", "Counter-intuitive", "Multi-step"]
    },
    "tagp": {
        "name": "TAGP",
        "title": "Trinity Attention Grid Pattern",
        "kaggle": "playra/trinity-tagp-adversarial",
        "file": "tagp_mc_aggressive.csv",
        "questions": 851,
        "expected_range": [20, 35],  # 20-35% for adversarial
        "features": ["Grid pattern breaking", "Memory interference", "Selective attention"]
    },
    "tefb": {
        "name": "TEFB",
        "title": "Trinity Executive Function Battery",
        "kaggle": "playra/trinity-tefb-cleaned",
        "file": "tefb_mc_cleaned.csv",
        "questions": 1512,
        "expected_range": [50, 70],  # 50-70% for cleaned
        "features": ["Planning", "Working memory", "Cognitive flexibility"]
    },
    "tscp": {
        "name": "TSCP",
        "title": "Trinity Social Cognition Protocol",
        "kaggle": "playra/trinity-tscp-cleaned",
        "file": "tscp_mc_cleaned.csv",
        "questions": 25,
        "expected_range": [60, 80],  # 60-80% for cleaned
        "features": ["Theory of mind", "Pragmatic inference", "Social reasoning"]
    }
}


@dataclass
class MCAnswer:
    """Schema for multiple choice answers."""
    answer: str


def load_track_data(track_id: str) -> pd.DataFrame:
    """Load and prepare adversarial dataset for a track."""
    config = DATASETS[track_id]
    path = f"/kaggle/input/{config['kaggle']}/{config['file']}"

    try:
        df = pd.read_csv(path)
        print(f"[{config['name']}] Loaded {len(df)} questions")
        return df
    except FileNotFoundError:
        print(f"[{config['name']}] Dataset not found at {path}")
        return None


# ========================================
# THLP: Pattern Learning
# ========================================

@kbench.task(name="thlp_adversarial_mc", store_task=False)
def thlp_adversarial_mc(llm, question: str, a: str, b: str, c: str, d: str, expected: str) -> bool:
    response = llm.prompt(f"Question: {question}\nA: {a}\nB: {b}\nC: {c}\nD: {d}\nAnswer (A/B/C/D):", schema=MCAnswer)
    got = response.answer.strip().upper()[:1]
    exp = expected.strip().upper()
    llm.logger.info(f"THLP | Got: {got} | Exp: {exp} | {'✓' if got==exp else '✗'}")
    return got == exp


@kbench.task(name="thlp_benchmark", description="THLP Adversarial Pattern Learning")
def thlp_benchmark(llm) -> Dict[str, Any]:
    df = load_track_data("thlp")
    if df is None: return {"error": "Dataset not found"}

    with kbench.client.enable_cache():
        runs = thlp_adversarial_mc.evaluate(llm=[llm], evaluation_data=df, n_jobs=2, timeout=180)

    results_df = runs.as_dataframe()
    valid = results_df[results_df['result'].notna()]
    accuracy = float(valid['result'].mean()) if len(valid) > 0 else 0
    in_range = DATASETS['thlp']['expected_range'][0] <= accuracy * 100 <= DATASETS['thlp']['expected_range'][1]

    metrics = {
        "track": "THLP", "total": len(valid), "correct": int(valid['result'].sum()),
        "accuracy": accuracy, "in_range": in_range, "questions": DATASETS['thlp']['questions']
    }
    print(f"THLP: {accuracy:.1%} ({int(valid['result'].sum())}/{len(valid)})")

    kbench.assertions.assert_true(accuracy > 0, expectation=f"THLP: {accuracy:.1%}")
    return metrics


# ========================================
# TTM: Metacognition
# ========================================

@kbench.task(name="ttm_physics_mc", store_task=False)
def ttm_physics_mc(llm, question: str, a: str, b: str, c: str, d: str, expected: str) -> bool:
    response = llm.prompt(f"Question: {question}\nA: {a}\nB: {b}\nC: {c}\nD: {d}\nAnswer (A/B/C/D):", schema=MCAnswer)
    got = response.answer.strip().upper()[:1]
    exp = expected.strip().upper()
    llm.logger.info(f"TTM | Got: {got} | Exp: {exp} | {'✓' if got==exp else '✗'}")
    return got == exp


@kbench.task(name="ttm_benchmark", description="TTM Physics-Enhanced Metacognition")
def ttm_benchmark(llm) -> Dict[str, Any]:
    df = load_track_data("ttm")
    if df is None: return {"error": "Dataset not found"}

    with kbench.client.enable_cache():
        runs = ttm_physics_mc.evaluate(llm=[llm], evaluation_data=df, n_jobs=2, timeout=180)

    results_df = runs.as_dataframe()
    valid = results_df[results_df['result'].notna()]
    accuracy = float(valid['result'].mean()) if len(valid) > 0 else 0
    in_range = DATASETS['ttm']['expected_range'][0] <= accuracy * 100 <= DATASETS['ttm']['expected_range'][1]

    metrics = {
        "track": "TTM", "total": len(valid), "correct": int(valid['result'].sum()),
        "accuracy": accuracy, "in_range": in_range, "questions": DATASETS['ttm']['questions']
    }
    print(f"TTM: {accuracy:.1%} ({int(valid['result'].sum())}/{len(valid)})")

    kbench.assertions.assert_true(accuracy > 0, expectation=f"TTM: {accuracy:.1%}")
    return metrics


# ========================================
# TAGP: Attention Control
# ========================================

@kbench.task(name="tagp_adversarial_mc", store_task=False)
def tagp_adversarial_mc(llm, question: str, a: str, b: str, c: str, d: str, expected: str) -> bool:
    response = llm.prompt(f"Question: {question}\nA: {a}\nB: {b}\nC: {c}\nD: {d}\nAnswer (A/B/C/D):", schema=MCAnswer)
    got = response.answer.strip().upper()[:1]
    exp = expected.strip().upper()
    llm.logger.info(f"TAGP | Got: {got} | Exp: {exp} | {'✓' if got==exp else '✗'}")
    return got == exp


@kbench.task(name="tagp_benchmark", description="TAGP Adversarial Attention Control")
def tagp_benchmark(llm) -> Dict[str, Any]:
    df = load_track_data("tagp")
    if df is None: return {"error": "Dataset not found"}

    with kbench.client.enable_cache():
        runs = tagp_adversarial_mc.evaluate(llm=[llm], evaluation_data=df, n_jobs=2, timeout=180)

    results_df = runs.as_dataframe()
    valid = results_df[results_df['result'].notna()]
    accuracy = float(valid['result'].mean()) if len(valid) > 0 else 0
    in_range = DATASETS['tagp']['expected_range'][0] <= accuracy * 100 <= DATASETS['tagp']['expected_range'][1]

    metrics = {
        "track": "TAGP", "total": len(valid), "correct": int(valid['result'].sum()),
        "accuracy": accuracy, "in_range": in_range, "questions": DATASETS['tagp']['questions']
    }
    print(f"TAGP: {accuracy:.1%} ({int(valid['result'].sum())}/{len(valid)})")

    kbench.assertions.assert_true(accuracy > 0, expectation=f"TAGP: {accuracy:.1%}")
    return metrics


# ========================================
# TEFB: Executive Functions
# ========================================

@kbench.task(name="tefb_cleaned_mc", store_task=False)
def tefb_cleaned_mc(llm, question: str, a: str, b: str, c: str, d: str, expected: str) -> bool:
    response = llm.prompt(f"Question: {question}\nA: {a}\nB: {b}\nC: {c}\nD: {d}\nAnswer (A/B/C/D):", schema=MCAnswer)
    got = response.answer.strip().upper()[:1]
    exp = expected.strip().upper()
    llm.logger.info(f"TEFB | Got: {got} | Exp: {exp} | {'✓' if got==exp else '✗'}")
    return got == exp


@kbench.task(name="tefb_benchmark", description="TEFB Cleaned Executive Function")
def tefb_benchmark(llm) -> Dict[str, Any]:
    df = load_track_data("tefb")
    if df is None: return {"error": "Dataset not found"}

    with kbench.client.enable_cache():
        runs = tefb_cleaned_mc.evaluate(llm=[llm], evaluation_data=df, n_jobs=2, timeout=180)

    results_df = runs.as_dataframe()
    valid = results_df[results_df['result'].notna()]
    accuracy = float(valid['result'].mean()) if len(valid) > 0 else 0
    in_range = DATASETS['tefb']['expected_range'][0] <= accuracy * 100 <= DATASETS['tefb']['expected_range'][1]

    metrics = {
        "track": "TEFB", "total": len(valid), "correct": int(valid['result'].sum()),
        "accuracy": accuracy, "in_range": in_range, "questions": DATASETS['tefb']['questions']
    }
    print(f"TEFB: {accuracy:.1%} ({int(valid['result'].sum())}/{len(valid)})")

    kbench.assertions.assert_true(accuracy > 0, expectation=f"TEFB: {accuracy:.1%}")
    return metrics


# ========================================
# TSCP: Social Cognition
# ========================================

@kbench.task(name="tscp_cleaned_mc", store_task=False)
def tscp_cleaned_mc(llm, question: str, a: str, b: str, c: str, d: str, expected: str) -> bool:
    response = llm.prompt(f"Question: {question}\nA: {a}\nB: {b}\nC: {c}\nD: {d}\nAnswer (A/B/C/D):", schema=MCAnswer)
    got = response.answer.strip().upper()[:1]
    exp = expected.strip().upper()
    llm.logger.info(f"TSCP | Got: {got} | Exp: {exp} | {'✓' if got==exp else '✗'}")
    return got == exp


@kbench.task(name="tscp_benchmark", description="TSCP Cleaned Social Cognition")
def tscp_benchmark(llm) -> Dict[str, Any]:
    df = load_track_data("tscp")
    if df is None: return {"error": "Dataset not found"}

    with kbench.client.enable_cache():
        runs = tscp_cleaned_mc.evaluate(llm=[llm], evaluation_data=df, n_jobs=2, timeout=180)

    results_df = runs.as_dataframe()
    valid = results_df[results_df['result'].notna()]
    accuracy = float(valid['result'].mean()) if len(valid) > 0 else 0
    in_range = DATASETS['tscp']['expected_range'][0] <= accuracy * 100 <= DATASETS['tscp']['expected_range'][1]

    metrics = {
        "track": "TSCP", "total": len(valid), "correct": int(valid['result'].sum()),
        "accuracy": accuracy, "in_range": in_range, "questions": DATASETS['tscp']['questions']
    }
    print(f"TSCP: {accuracy:.1%} ({int(valid['result'].sum())}/{len(valid)})")

    kbench.assertions.assert_true(accuracy > 0, expectation=f"TSCP: {accuracy:.1%}")
    return metrics


# ========================================
# All-Tracks Benchmark
# ========================================

@kbench.task(name="trinity_all_tracks", description="Trinity Cognitive Probes - All 5 Tracks")
def trinity_all_tracks_benchmark(llm) -> Dict[str, Any]:
    """
    Run all 5 Trinity cognitive benchmarks.

    This comprehensive benchmark evaluates:
    - THLP: Pattern learning (adversarial)
    - TTM: Metacognition (physics-enhanced)
    - TAGP: Attention control (adversarial)
    - TEFB: Executive functions (cleaned)
    - TSCP: Social cognition (cleaned)

    Total: 2,861 questions
    """
    print("\n" + "="*60)
    print("TRINITY COGNITIVE PROBES - ALL TRACKS BENCHMARK")
    print("="*60)

    all_results = {}
    total_questions = 0
    total_correct = 0

    # Run each track
    for track_id in ["thlp", "ttm", "tagp", "tefb", "tscp"]:
        config = DATASETS[track_id]
        print(f"\n{'='*60}")
        print(f"Track: {config['title']}")
        print(f"Dataset: {config['kaggle']}")
        print(f"Expected accuracy: {config['expected_range'][0]}-{config['expected_range'][1]}%")
        print(f"{'='*60}")

        df = load_track_data(track_id)
        if df is None:
            print(f"Skipping {track_id} - dataset not found")
            continue

        # Get benchmark function
        benchmark_fn = globals()[f"{track_id}_benchmark"]

        try:
            with kbench.client.enable_cache():
                task_fn = globals()[f"{track_id}_adversarial_mc" if track_id in ["thlp", "tagp"] else f"{track_id}_cleaned_mc" if track_id in ["tefb", "tscp"] else f"{track_id}_physics_mc"
                runs = task_fn.evaluate(llm=[llm], evaluation_data=df, n_jobs=2, timeout=180)

            results_df = runs.as_dataframe()
            valid = results_df[results_df['result'].notna()]

            track_total = len(valid)
            track_correct = int(valid['result'].sum())
            track_accuracy = float(valid['result'].mean()) if track_total > 0 else 0

            all_results[track_id] = {
                "total": track_total,
                "correct": track_correct,
                "accuracy": track_accuracy,
                "in_range": config['expected_range'][0] <= track_accuracy * 100 <= config['expected_range'][1]
            }

            total_questions += track_total
            total_correct += track_correct

            print(f"Result: {track_accuracy:.1%} ({track_correct}/{track_total})")

        except Exception as e:
            print(f"Error running {track_id}: {e}")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    overall_accuracy = total_correct / total_questions if total_questions > 0 else 0

    for track_id, result in all_results.items():
        status = "✓" if result['in_range'] else "✗"
        config = DATASETS[track_id]
        print(f"{status} {config['name']:8s}: {result['accuracy']:5.1%} "
              f"({result['correct']:3d}/{result['total']:3d}) "
              f"[{config['expected_range'][0]}-{config['expected_range'][1]}%]")

    print("-" * 60)
    print(f"Overall: {overall_accuracy:.1%} ({total_correct}/{total_questions})")
    print(f"Total questions: {total_questions}")

    # Assertions
    kbench.assertions.assert_true(
        overall_accuracy > 0,
        expectation=f"Trinity overall accuracy: {overall_accuracy:.1%}"
    )

    return {
        "overall_accuracy": overall_accuracy,
        "total_questions": total_questions,
        "total_correct": total_correct,
        "track_results": all_results
    }


if __name__ == "__main__":
    run = trinity_all_tracks_benchmark.run(kbench.llm)
