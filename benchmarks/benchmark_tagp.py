import os
import re
import pandas as pd
import kaggle_benchmarks as kbench

# Reduce sub-run verbosity for large datasets
os.environ["RENDER_SUBRUNS"] = "False"

# ---- Load dataset ----
# In Kaggle notebook, add dataset playra/trinity-cognitive-probes-tagp-mc as input
df = pd.read_csv("/kaggle/input/trinity-cognitive-probes-tagp-mc/tagp_mc_fixed.csv")

# Clean and sample
df = df.dropna(subset=["question", "choices", "answer"])
df["answer"] = df["answer"].str.strip().str.upper()
df = df[df["answer"].isin(["A", "B", "C", "D"])]

# Sample 200 questions for benchmark (representative, reproducible)
# Dataset has 2,200 questions — sample for efficient evaluation
df = df.sample(n=min(200, len(df)), random_state=42).reset_index(drop=True)

print(f"Loaded {len(df)} questions for TAGP (Attention) benchmark")

# ---- Define sub-task for single question ----
@kbench.task(store_task=False)
def single_mc_question(llm, question: str, choices: str, answer: str) -> bool:
    """Evaluate a single MC question."""
    prompt = f"""You are taking a cognitive assessment. Read the question and choices carefully, then respond with ONLY the letter of the correct answer (A, B, C, or D). Do not explain.

Question: {question}

{choices}

Answer:"""

    with kbench.chats.new("mc_question"):
        response = llm.prompt(prompt)

    # Parse the model's answer
    response_clean = response.strip().upper()
    predicted = ""

    # Direct single letter
    if response_clean in ("A", "B", "C", "D"):
        predicted = response_clean
    else:
        # Look for A), B), C), D) pattern
        match = re.search(r'\b([ABCD])\b', response_clean)
        if match:
            predicted = match.group(1)

    is_correct = predicted == answer.strip().upper()
    return is_correct


# ---- Define main benchmark task ----
@kbench.task(name="trinity_tagp_benchmark")
def trinity_tagp_benchmark(llm, df: pd.DataFrame) -> tuple[float, float]:
    """Trinity Top-Down Attentional Gating Probe (TAGP) Benchmark.

    Evaluates attentional control and focus allocation across 200 multiple-choice
    questions testing selective filtering, sustained attention, and attention
    shifting under competing stimuli.

    Brain Zones: Parietal Cortex, Frontal Eye Field (FEF)
    """
    with kbench.client.enable_cache():
        runs = single_mc_question.evaluate(
            stop_condition=lambda runs: len(runs) == df.shape[0],
            max_attempts=df.shape[0] * 3,
            retry_delay=10,
            llm=[llm],
            evaluation_data=df[["question", "choices", "answer"]],
            n_jobs=4,
            timeout=300,
            remove_run_files=True,
        )

    eval_df = runs.as_dataframe()
    accuracy = float(eval_df["result"].mean())
    std = float(eval_df["result"].std())

    # Report results
    n_correct = int(eval_df["result"].sum())
    n_total = len(eval_df)
    print(f"\nResults: {n_correct}/{n_total} correct ({accuracy:.1%})")
    print(f"Accuracy: {accuracy:.4f} ± {std:.4f}")

    return accuracy, std


# ---- Run benchmark ----
run = trinity_tagp_benchmark.run(kbench.llm, df)
run

# ---- Select task for leaderboard ----
# %choose trinity_tagp_benchmark
