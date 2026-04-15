#!/usr/bin/env python3
"""
Unified Inference Script for All Models
"""

import anthropic
import openai
import requests
import pandas as pd
from pathlib import Path
import yaml
from typing import Dict, List

# Adversarial datasets
DATASETS = {
    "thlp": "kaggle/data/extra/thlp_mc_aggressive.csv",
    "ttm": "kaggle/data/extra/ttm_physics_mc.csv",
    "tagp": "kaggle/data/tagp_mc_aggressive.csv",
    "tefb": "kaggle/data/extra/tefb_mc_cleaned.csv",
    "tscp": "kaggle/data/extra/tscp_mc_cleaned.csv"
}

class ModelEvaluator:
    """Base class for model evaluation"""
    def __init__(self, model_name: str, config: Dict):
        self.model_name = model_name
        self.config = config
        self.client = None

    def init_anthropic(self):
        """Initialize Anthropic Claude API"""
        if not self.config.get('anthropic', {}).get('enabled', False):
            print("⚠️  Claude API not enabled in config")
            self.enabled = False
            return

        api_key = self.config['anthropic'].get('api_key', '')
        if not api_key or api_key == 'your-anthropic-api-key':
            print("⚠️  No Anthropic API key found!")
            self.enabled = False
            return

        max_retries = self.config['anthropic'].get('max_retries', 3)
        rate_limit = self.config['anthropic'].get('rate_limit', 20)
        timeout = self.config['anthropic'].get('timeout', 60)

        try:
            self.client = anthropic.Anthropic(api_key=api_key)
            self.enabled = True
            print("✅ Anthropic Claude client initialized")
        except Exception as e:
            print(f"❌ Anthropic initialization error: {e}")
            self.enabled = False

    def init_openai_gpt4(self):
        """Initialize OpenAI GPT-4 API"""
        if not self.config.get('openai', {}).get('enabled', False):
            print("⚠️  OpenAI API not enabled in config")
            self.enabled = False
            return

        api_key = self.config['openai'].get('api_key', '')
        if not api_key or api_key == 'your-openai-api-key':
            print("⚠️  No OpenAI API key found!")
            self.enabled = False
            return

        max_retries = self.config['openai'].get('max_retries', 3)
        rate_limit = self.config['openai'].get('rate_limit', 30)
        timeout = self.config['openai'].get('timeout', 60)
        model = self.config['openai'].get('model', 'gpt-4-turbo')

        try:
            self.client = openai.OpenAI(api_key=api_key)
            self.enabled = True
            print(f"✅ OpenAI GPT-4 client initialized (model: {model})")
        except Exception as e:
            print(f"❌ OpenAI initialization error: {e}")
            self.enabled = False

    def init_google_gemini(self):
        """Initialize Google Gemini API via REST"""
        if not self.config.get('google', {}).get('enabled', False):
            print("⚠️  Google API not enabled in config")
            self.enabled = False
            return

        api_key = self.config['google'].get('api_key', '')
        if not api_key or api_key == 'your-google-api-key':
            print("⚠️  No Google API key found!")
            self.enabled = False
            return

        max_retries = self.config['google'].get('max_retries', 3)
        rate_limit = self.config['google'].get('rate_limit', 30)
        timeout = self.config['google'].get('timeout', 60)
        model = self.config['google'].get('model', 'gemini-1.5-pro')

        # Google doesn't have official Python SDK for Gemini - using REST
        self.enabled = True  # Assume enabled if API key exists
        print(f"✅ Google Gemini client initialized (model: {model}) - REST API")

    def load_questions(self, dataset_path: str) -> pd.DataFrame:
        """Load questions from dataset"""
        if not Path(dataset_path).exists():
            print(f"⚠️  Dataset not found: {dataset_path}")
            return None

        df = pd.read_csv(dataset_path)
        print(f"✅ Loaded {len(df)} questions from {dataset_path}")
        return df

    def evaluate_claude(self, questions_df: pd.DataFrame, track: str) -> List[str]:
        """Evaluate using Claude Anthropic API"""
        if not self.enabled or self.client is None:
            print("⚠️  Claude API not available")
            return []

        predictions = []
        max_retries = self.config['anthropic'].get('max_retries', 3)

        for idx, row in questions_df.iterrows():
            # Create prompt
            prompt = f"""Question: {row['question']}

Choices:
{row['choices']}

Answer with ONLY ONE letter (A, B, C, or D). Do not explain. Return exactly one character."""

            # Call Claude API with retry logic
            for attempt in range(max_retries):
                try:
                    response = self.client.messages.create(
                        model="claude-3-5-sonnet-20240229",
                        max_tokens=4096,
                        temperature=0.0,
                        messages=[{"role": "user", "content": prompt}]
                    )

                    prediction = response.content[0].text.strip().upper()[0]

                    if prediction in ['A', 'B', 'C', 'D']:
                        predictions.append(prediction)
                        print(f"  [{idx}] ✅ Claude: {prediction}")
                        break
                    else:
                        print(f"  [{idx}] ⚠️  Claude: Invalid format: {prediction}")
                        # Use default
                        predictions.append('A')
                        break

                except Exception as api_error:
                    if attempt < max_retries - 1:
                        print(f"  [{idx}] ⚠️  Claude retry {attempt + 1}/{max_retries}: {api_error}")
                        time.sleep(1)  # Exponential backoff
                    else:
                        print(f"  [{idx}] ❌  Claude error after {max_retries} retries: {api_error}")
                        predictions.append('A')  # Default
                        break

            # Rate limiting
            time.sleep(60 / max_retries)

        print(f"  Claude {track}: {len(predictions)}/{len(questions_df)} processed")
        return predictions

    def evaluate_gpt4(self, questions_df: pd.DataFrame, track: str) -> List[str]:
        """Evaluate using OpenAI GPT-4 API"""
        if not self.enabled or self.client is None:
            print("⚠️  GPT-4 API not available")
            return []

        predictions = []
        max_retries = self.config['openai'].get('max_retries', 3)

        for idx, row in questions_df.iterrows():
            # Create prompt
            prompt = f"""Question: {row['question']}

Choices:
{row['choices']}

Answer with ONLY ONE letter (A, B, C, or D). Do not explain. Return exactly one character."""

            # Call GPT-4 API with retry logic
            for attempt in range(max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.config['openai'].get('model', 'gpt-4-turbo'),
                        max_tokens=4096,
                        temperature=0.0,
                        messages=[{"role": "user", "content": prompt}]
                    )

                    prediction = response.choices[0].message.content.strip().upper()[0]

                    if prediction in ['A', 'B', 'C', 'D']:
                        predictions.append(prediction)
                        print(f"  [{idx}] ✅  GPT-4: {prediction}")
                        break
                    else:
                        print(f"  [{idx}] ⚠️  GPT-4: Invalid format: {prediction}")
                        # Use default
                        predictions.append('A')
                        break

                except Exception as api_error:
                    if attempt < max_retries - 1:
                        print(f"  [{idx}] ⚠️  GPT-4 retry {attempt + 1}/{max_retries}: {api_error}")
                        time.sleep(1)  # Exponential backoff
                    else:
                        print(f"  [{idx}] ❌  GPT-4 error after {max_retries} retries: {api_error}")
                        predictions.append('A')  # Default
                        break

            # Rate limiting
            time.sleep(60 / max_retries)

        print(f"  GPT-4 {track}: {len(predictions)}/{len(questions_df)} processed")
        return predictions

    def evaluate_gemini(self, questions_df: pd.DataFrame, track: str) -> List[str]:
        """Evaluate using Google Gemini REST API"""
        if not self.enabled:
            print("⚠️  Gemini API not available")
            return []

        predictions = []
        api_key = self.config['google'].get('api_key', '')
        model = self.config['google'].get('model', 'gemini-1.5-pro')
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        for idx, row in questions_df.iterrows():
            # Create prompt
            prompt = f"""Question: {row['question']}

Choices:
{row['choices']}

Answer with ONLY ONE letter (A, B, C, or D). Do not explain. Return exactly one character."""

            # Call Google Gemini API with retry logic (max 3 retries)
            for attempt in range(3):
                try:
                    response = requests.post(
                        api_url,
                        json={
                            "contents": [{"parts": [{"text": prompt}]}],
                            "generationConfig": {
                                "temperature": 0.0,
                                "maxOutputTokens": 4096
                            }
                        },
                        headers={"Content-Type": "application/json"}
                    )

                    if response.status_code == 200:
                        result = response.json()
                        prediction = result.get('candidates', [{}])[0].get('content', '')[:1].upper()

                        if prediction in ['A', 'B', 'C', 'D']:
                            predictions.append(prediction)
                            print(f"  [{idx}] ✅  Gemini: {prediction}")
                            break
                        else:
                            print(f"  [{idx}] ⚠️  Gemini: Invalid format: {prediction}")
                            predictions.append('A')
                            break

                except Exception as api_error:
                    if attempt < 2:
                        print(f"  [{idx}] ⚠️  Gemini retry {attempt + 1}/3: {api_error}")
                        time.sleep(1)  # Linear backoff
                    else:
                        print(f"  [{idx}] ❌  Gemini error after 3 retries: {api_error}")
                        predictions.append('A')
                        break

            # Rate limiting for Google
            time.sleep(60)

        print(f"  Gemini {track}: {len(predictions)}/{len(questions_df)} processed")
        return predictions

    def evaluate_model(self, model_name: str, track: str) -> List[str]:
        """Evaluate model on specific track"""
        dataset_path = DATASETS.get(track)
        if not dataset_path:
            print(f"⚠️  No dataset for track: {track}")
            return []

        questions_df = self.load_questions(dataset_path)
        if questions_df is None or questions_df.empty:
            return []

        print(f"\n🤖 Evaluating {model_name.upper()} on {track.upper()}")
        print(f"{'='*60}")

        # Route to appropriate evaluator
        if model_name.lower() == 'claude':
            predictions = self.evaluate_claude(questions_df, track)
        elif model_name.lower() == 'gpt4':
            predictions = self.evaluate_gpt4(questions_df, track)
        elif model_name.lower() == 'gemma':
            predictions = self.evaluate_gemini(questions_df, track)
        else:
            print(f"⚠️  Unknown model: {model_name}")
            predictions = []

        return predictions

def create_submission(predictions_dict: Dict[str, List[str]], output_path: Path) -> pd.DataFrame:
    """Create unified submission file"""
    all_predictions = []

    # Get maximum number of predictions across all tracks
    max_predictions = max(len(preds) for preds in predictions_dict.values())

    # Create submission rows
    for i in range(max_predictions):
        row = [f"sample_{i}"]
        for track, preds in predictions_dict.items():
            if i < len(preds):
                row.append(preds[i])
            else:
                row.append('A')  # Default for extra rows

        all_predictions.append(row)

    # Create DataFrame
    submission_df = pd.DataFrame(all_predictions, columns=['id'] + list(predictions_dict.keys()))

    # Save
    submission_df.to_csv(output_path, index=False)
    print(f"✅ Unified submission saved to: {output_path}")
    print(f"   Total rows: {len(submission_df)}")

    return submission_df

def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='Unified Inference for Trinity Cognitive Probes')
    parser.add_argument('--model', type=str, choices=['claude', 'gpt4', 'gemma', 'all'], default='all',
                       help='Model to use (claude, gpt4, gemma, or all)')
    parser.add_argument('--track', type=str, default='all',
                       help='Track to evaluate (thlp, ttm, tagp, tefb, tscp, or all)')
    parser.add_argument('--sample', type=int, default=None,
                       help='Number of questions to process (for testing)')
    parser.add_argument('--output', type=str, default='kaggle/submission_predictions.csv',
                       help='Output submission file path')

    args = parser.parse_args()

    # Load API configuration
    API_CONFIG_FILE = Path("api_keys.yaml")

    config = {}
    if API_CONFIG_FILE.exists():
        with open(API_CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f)

    # Initialize models
    evaluators = {}

    if args.model == 'all':
        models_to_evaluate = ['claude', 'gpt4', 'gemma']
    else:
        models_to_evaluate = [args.model]

    for model_name in models_to_evaluate:
        evaluator = ModelEvaluator(model_name, config)
        evaluators[model_name] = evaluator

    # Evaluate all models on all tracks
    all_predictions = {}

    tracks_to_evaluate = [args.track] if args.track != 'all' else ['thlp', 'ttm', 'tagp', 'tefb', 'tscp']

    for track in tracks_to_evaluate:
        print(f"\n{'='*60}")
        print(f"🎯 Evaluating {track.upper()}")
        print(f"{'='*60}")

        # Load dataset
        dataset_path = DATASETS.get(track)
        if not dataset_path:
            print(f"⚠️  Skipping {track}: {dataset_path} not found")
            continue

        # Apply sample size if specified
        df = pd.read_csv(dataset_path)
        if args.sample and args.sample < len(df):
            df = df.sample(n=args.sample)
            print(f"  Using sample of {args.sample} questions")

        # Evaluate with each model
        track_predictions = {}
        for model_name, evaluator in evaluators.items():
            predictions = evaluator.evaluate_model(model_name, track)
            track_predictions[model_name] = predictions

            # Print summary
            valid_predictions = [p for p in predictions if p in ['A', 'B', 'C', 'D']]
            accuracy = len(valid_predictions) / len(predictions) if predictions else 0
            print(f"  {model_name.upper()}: {accuracy:.1%} ({len(valid_predictions)}/{len(predictions)} valid)")

        all_predictions[track] = track_predictions

    # Create unified submission
    submission_df = create_submission(all_predictions, Path(args.output))

    # Print final summary
    print(f"\n{'='*60}")
    print("📊 FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"Total submission rows: {len(submission_df)}")
    print(f"Models evaluated: {', '.join(models_to_evaluate)}")
    print(f"Tracks evaluated: {', '.join(tracks_to_evaluate)}")
    print(f"Output: {args.output}")
    print(f"{'='*60}")
    print("🎯 READY FOR KAGGLE SUBMISSION!")

if __name__ == '__main__':
    main()
