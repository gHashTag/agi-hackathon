#!/usr/bin/env python3
"""
Inference script for AGI Hackathon adversarial datasets.

This script runs model inference on all 5 adversarial datasets:
- THLP: Adversarial (274 questions)
- TTM: Physics Enhanced (199 questions)
- TAGP: Adversarial (851 questions)
- TEFB: Cleaned (1,512 questions)
- TSCP: Cleaned (25 questions)

Supported models:
- Claude 3.5 Sonnet (Anthropic)
- GPT-4o (OpenAI)
- Gemini 1.5 Flash (Google)

Usage:
    python3 scripts/inference.py --model gpt-4o --track all
    python3 scripts/inference.py --model claude --track thlp --output results/
"""

import os
import sys
import argparse
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Track configurations
TRACKS = {
    "thlp": {
        "name": "THLP",
        "title": "Trinity Hierarchical Learning Pattern",
        "source": "kaggle/data/extra/thlp_mc_aggressive.csv",
        "kaggle": "playra/trinity-thlp-adversarial",
        "expected_accuracy": "25-40%"
    },
    "ttm": {
        "name": "TTM",
        "title": "Trinity Metacognitive",
        "source": "kaggle/data/extra/ttm_physics_mc.csv",
        "kaggle": "playra/trinity-ttm-physics-enhanced",
        "expected_accuracy": "10-25%"
    },
    "tagp": {
        "name": "TAGP",
        "title": "Trinity Attention Grid Pattern",
        "source": "kaggle/data/tagp_mc_aggressive.csv",
        "kaggle": "playra/trinity-tagp-adversarial",
        "expected_accuracy": "20-35%"
    },
    "tefb": {
        "name": "TEFB",
        "title": "Trinity Executive Function Battery",
        "source": "kaggle/data/extra/tefb_mc_cleaned.csv",
        "kaggle": "playra/trinity-tefb-cleaned",
        "expected_accuracy": "50-70%"
    },
    "tscp": {
        "name": "TSCP",
        "title": "Trinity Social Cognition Protocol",
        "source": "kaggle/data/extra/tscp_mc_cleaned.csv",
        "kaggle": "playra/trinity-tscp-cleaned",
        "expected_accuracy": "60-80%"
    },
}


class ModelInterface:
    """Base interface for LLM inference."""

    def __init__(self, model_name: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key or os.environ.get(self._get_env_key())
        self.client = None
        self._initialize_client()

    def _get_env_key(self) -> str:
        """Get the environment variable name for the API key."""
        raise NotImplementedError

    def _initialize_client(self):
        """Initialize the API client."""
        raise NotImplementedError

    def predict(self, question: str, choices: Dict[str, str]) -> str:
        """
        Predict answer for a multiple choice question.

        Args:
            question: The question text
            choices: Dict of choice letters to choice text

        Returns:
            The predicted answer letter (A, B, C, or D)
        """
        raise NotImplementedError


class ClaudeModel(ModelInterface):
    """Claude 3.5 Sonnet via Anthropic API."""

    def _get_env_key(self) -> str:
        return "ANTHROPIC_API_KEY"

    def _initialize_client(self):
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
            print(f"✓ Initialized Claude client")
        except ImportError:
            print("✗ anthropic package not installed")
            raise

    def predict(self, question: str, choices: Dict[str, str]) -> str:
        prompt = self._build_prompt(question, choices)

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.content[0].text.strip().upper()[0]
            return answer if answer in ['A', 'B', 'C', 'D'] else 'A'
        except Exception as e:
            print(f"✗ Error: {e}")
            return 'A'

    def _build_prompt(self, question: str, choices: Dict[str, str]) -> str:
        choices_text = "\n".join([
            f"{k}: {choices.get(k, '')}"
            for k in sorted(choices.keys())
        ])
        return f"""Answer the following multiple choice question with ONLY ONE letter (A, B, C, or D).

Question: {question}

Choices:
{choices_text}

Your answer (A/B/C/D):"""


class GPT4Model(ModelInterface):
    """GPT-4o via OpenAI API."""

    def _get_env_key(self) -> str:
        return "OPENAI_API_KEY"

    def _initialize_client(self):
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")

        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            print(f"✓ Initialized OpenAI client")
        except ImportError:
            print("✗ openai package not installed")
            raise

    def predict(self, question: str, choices: Dict[str, str]) -> str:
        prompt = self._build_prompt(question, choices)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.0
            )
            answer = response.choices[0].message.content.strip().upper()[0]
            return answer if answer in ['A', 'B', 'C', 'D'] else 'A'
        except Exception as e:
            print(f"✗ Error: {e}")
            return 'A'

    def _build_prompt(self, question: str, choices: Dict[str, str]) -> str:
        choices_text = "\n".join([
            f"{k}: {choices.get(k, '')}"
            for k in sorted(choices.keys())
        ])
        return f"""Answer the following multiple choice question with ONLY ONE letter (A, B, C, or D).

Question: {question}

Choices:
{choices_text}

Your answer (A/B/C/D):"""


class GeminiModel(ModelInterface):
    """Gemini 1.5 Flash via Google API."""

    def _get_env_key(self) -> str:
        return "GOOGLE_API_KEY"

    def _initialize_client(self):
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set")

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel("gemini-1.5-flash")
            print(f"✓ Initialized Gemini client")
        except ImportError:
            print("✗ google-generativeai package not installed")
            raise

    def predict(self, question: str, choices: Dict[str, str]) -> str:
        prompt = self._build_prompt(question, choices)

        try:
            response = self.client.generate_content(
                prompt,
                generation_config={"max_output_tokens": 10}
            )
            answer = response.text.strip().upper()[0]
            return answer if answer in ['A', 'B', 'C', 'D'] else 'A'
        except Exception as e:
            print(f"✗ Error: {e}")
            return 'A'

    def _build_prompt(self, question: str, choices: Dict[str, str]) -> str:
        choices_text = "\n".join([
            f"{k}: {choices.get(k, '')}"
            for k in sorted(choices.keys())
        ])
        return f"""Answer the following multiple choice question with ONLY ONE letter (A, B, C, or D).

Question: {question}

Choices:
{choices_text}

Your answer (A/B/C/D):"""


# Model registry
MODELS = {
    "claude": ClaudeModel,
    "gpt-4o": GPT4Model,
    "gpt4": GPT4Model,
    "gemini": GeminiModel,
}


def load_dataset(track: str) -> pd.DataFrame:
    """Load dataset for a specific track."""
    track_config = TRACKS[track]
    source_file = track_config["source"]

    if not os.path.exists(source_file):
        raise FileNotFoundError(f"Dataset not found: {source_file}")

    df = pd.read_csv(source_file)
    print(f"✓ Loaded {len(df)} questions from {track}")

    return df


def evaluate_track(model: ModelInterface, df: pd.DataFrame,
                  track: str, sample_size: Optional[int] = None) -> pd.DataFrame:
    """
    Run inference on a track's dataset.

    Args:
        model: The model to use for inference
        df: The dataset
        track: Track name
        sample_size: If set, only evaluate this many questions (for testing)

    Returns:
        DataFrame with predictions
    """
    print(f"\nEvaluating {TRACKS[track]['title']}...")

    if sample_size:
        df = df.head(sample_size)
        print(f"Using sample of {sample_size} questions")

    results = []

    for idx, row in df.iterrows():
        question = row.get('question', '')
        choices = {
            'A': row.get('A', ''),
            'B': row.get('B', ''),
            'C': row.get('C', ''),
            'D': row.get('D', '')
        }
        correct_answer = str(row.get('answer', '')).strip().upper()

        predicted = model.predict(question, choices)
        is_correct = predicted == correct_answer

        results.append({
            'id': row.get('id', idx),
            'question': question[:50] + '...' if len(question) > 50 else question,
            'predicted': predicted,
            'correct': correct_answer,
            'is_correct': is_correct
        })

        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1}/{len(df)} questions...")

    return pd.DataFrame(results)


def calculate_metrics(results: pd.DataFrame) -> Dict:
    """Calculate evaluation metrics."""
    total = len(results)
    correct = results['is_correct'].sum()
    accuracy = correct / total if total > 0 else 0.0

    # Per-class accuracy
    class_accuracy = {}
    for answer in ['A', 'B', 'C', 'D']:
        subset = results[results['correct'] == answer]
        if len(subset) > 0:
            class_accuracy[answer] = {
                'total': len(subset),
                'correct': subset['is_correct'].sum(),
                'accuracy': subset['is_correct'].mean()
            }

    return {
        'total_questions': int(total),
        'correct_answers': int(correct),
        'accuracy': float(accuracy),
        'class_accuracy': class_accuracy
    }


def save_submission(results: pd.DataFrame, track: str, output_dir: str):
    """Save predictions to submission format."""
    output_path = os.path.join(output_dir, f"submission_{track}.csv")

    submission = results[['id', 'predicted']].copy()
    submission.columns = ['id', 'prediction']
    submission.to_csv(output_path, index=False)

    print(f"✓ Saved submission to {output_path}")


def save_results(results: pd.DataFrame, metrics: Dict,
                track: str, model_name: str, output_dir: str):
    """Save full results and metrics."""
    results_path = os.path.join(output_dir, f"results_{track}_{model_name}.csv")
    results.to_csv(results_path, index=False)

    metrics_path = os.path.join(output_dir, f"metrics_{track}_{model_name}.json")
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"✓ Saved results to {results_path}")
    print(f"✓ Saved metrics to {metrics_path}")


def combine_submissions(output_dir: str):
    """Combine all track submissions into one file."""
    submissions = []

    for track in TRACKS.keys():
        submission_path = os.path.join(output_dir, f"submission_{track}.csv")
        if os.path.exists(submission_path):
            df = pd.read_csv(submission_path)
            df['track'] = track
            submissions.append(df)

    if not submissions:
        print("No submissions found to combine")
        return

    combined = pd.concat(submissions, ignore_index=True)

    # Add global IDs
    combined['global_id'] = combined['track'] + '_' + combined['id'].astype(str)

    combined_path = os.path.join(output_dir, "submission.csv")
    combined.to_csv(combined_path, index=False)

    print(f"\n✓ Combined submission saved to {combined_path}")
    print(f"  Total: {len(combined)} questions across {len(submissions)} tracks")


def main():
    parser = argparse.ArgumentParser(
        description="Run inference on AGI Hackathon adversarial datasets"
    )
    parser.add_argument(
        "--model", "-m",
        required=True,
        choices=list(MODELS.keys()),
        help="Model to use for inference"
    )
    parser.add_argument(
        "--track", "-t",
        default="all",
        choices=list(TRACKS.keys()) + ["all"],
        help="Track to evaluate (default: all)"
    )
    parser.add_argument(
        "--output", "-o",
        default="inference_results",
        help="Output directory for results"
    )
    parser.add_argument(
        "--sample", "-s",
        type=int,
        help="Sample size for testing (evaluates only first N questions)"
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize model
    print("="*60)
    print(f"INFERENCE WITH {args.model.upper()}")
    print("="*60)

    try:
        model_class = MODELS[args.model]
        model = model_class(args.model)
    except ValueError as e:
        print(f"✗ Error initializing model: {e}")
        sys.exit(1)

    # Evaluate tracks
    tracks_to_run = list(TRACKS.keys()) if args.track == "all" else [args.track]

    all_metrics = {}

    for track in tracks_to_run:
        print(f"\n{'='*60}")
        print(f"TRACK: {TRACKS[track]['name']}")
        print(f"Dataset: {TRACKS[track]['source']}")
        print(f"{'='*60}")

        try:
            df = load_dataset(track)
            results = evaluate_track(model, df, track, args.sample)
            metrics = calculate_metrics(results)

            print(f"\nResults:")
            print(f"  Accuracy: {metrics['accuracy']:.2%}")
            print(f"  Correct: {metrics['correct_answers']}/{metrics['total_questions']}")

            save_submission(results, track, str(output_dir))
            save_results(results, metrics, track, args.model, str(output_dir))

            all_metrics[track] = metrics

        except FileNotFoundError as e:
            print(f"✗ Skipping: {e}")

    # Combine submissions
    if args.track == "all":
        combine_submissions(str(output_dir))

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    for track, metrics in all_metrics.items():
        print(f"{TRACKS[track]['name']:8s}: {metrics['accuracy']:5.1%} "
              f"({metrics['correct_answers']:3d}/{metrics['total_questions']:3d})")


if __name__ == "__main__":
    main()
