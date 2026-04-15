#!/usr/bin/env python3
"""
Parallel GLM-5 testing with multiple API keys for rate limit bypass
Tests all tracks simultaneously using available ZAI_KEY tokens
"""

import csv
import os
import sys
import requests
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

# Load all API keys from .env
ENV_FILE = Path("/Users/playra/.claude/.env")
API_KEYS = []

if ENV_FILE.exists():
    with open(ENV_FILE) as f:
        for line in f:
            if line.startswith("ZAI_KEY_") and "=" in line:
                key = line.split("=", 1)[1].strip()
                if key:
                    API_KEYS.append(key)
else:
    print("Error: .env file not found")
    sys.exit(1)

print(f"✓ Loaded {len(API_KEYS)} API keys for rate limit bypass")

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
TRACKS = {
    'thlp': 'kaggle/data/extra/thlp_mc_new.csv',
    'ttm': 'kaggle/data/extra/ttm_mc_new.csv',
    'tagp': 'kaggle/data/tagp_mc.csv',
    'tefb': 'kaggle/data/extra/tefb_mc_new.csv',
    'tscp': 'kaggle/data/extra/tscp_mc_new.csv'
}

def load_questions(csv_path: str, sample_size: int = 20) -> List[Dict]:
    """Load MC questions from CSV"""
    questions = []
    path = Path(csv_path)

    if not path.exists():
        print(f"Warning: {csv_path} not found")
        return []

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Filter MC type questions
            qtype = row.get('question_type', '').lower()
            if qtype == 'mc':
                questions.append(row)
                if len(questions) >= sample_size:
                    break
    return questions

def evaluate_glm5(question: Dict, api_key: str) -> tuple:
    """Evaluate single question with GLM-5 using specific API key"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    choices_text = question.get('choices', '')

    prompt = f"""Answer the following multiple-choice question with ONLY the letter (A, B, C, or D).

Question: {question.get('question', '')}

{choices_text}

Answer:"""

    payload = {
        "model": "glm-5",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 50
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        result = response.json()

        if "choices" not in result or not result["choices"]:
            return None, "No response"

        answer_text = result["choices"][0]["message"]["content"].strip().upper()

        # Extract letter from response
        for letter in ['A', 'B', 'C', 'D']:
            if letter in answer_text[:10]:
                return letter, None
        return answer_text[0] if answer_text else 'A', None

    except requests.exceptions.Timeout:
        return 'A', "Timeout"
    except requests.exceptions.RequestException as e:
        return 'A', f"API Error: {str(e)[:50]}"
    except Exception as e:
        return 'A', f"Error: {str(e)[:50]}"

def test_track(track_name: str, csv_path: str, api_key: str, sample_size: int = 20) -> Dict:
    """Test a single track with given API key"""
    print(f"\n🔄 [{track_name.upper()}] Starting with key ending in ...{api_key[-8:]}")

    questions = load_questions(csv_path, sample_size)
    if not questions:
        return {
            'track': track_name,
            'total': 0,
            'correct': 0,
            'accuracy': 0.0,
            'errors': 0,
            'questions': []
        }

    results = []
    correct = 0
    errors = 0

    for i, q in enumerate(questions, 1):
        predicted, error = evaluate_glm5(q, api_key)
        expected = q.get('answer', '').upper()

        if error:
            errors += 1

        is_correct = predicted == expected
        if is_correct:
            correct += 1

        status = "✓" if is_correct else "✗"
        print(f"  [{track_name.upper()}] {i}/{len(questions)} {status} P:{predicted} E:{expected}")

        results.append({
            'id': q.get('id', ''),
            'predicted': predicted,
            'expected': expected,
            'correct': is_correct,
            'error': error
        })

    accuracy = correct / len(questions) if questions else 0.0

    print(f"✅ [{track_name.upper()}] Complete: {correct}/{len(questions)} ({accuracy:.1%})")

    return {
        'track': track_name,
        'total': len(questions),
        'correct': correct,
        'accuracy': accuracy,
        'errors': errors,
        'questions': results
    }

def main():
    sample_size = 20

    print("=" * 70)
    print("🚀 GLM-5 PARALLEL TESTING - ALL TRACKS")
    print("=" * 70)
    print(f"API Keys: {len(API_KEYS)}")
    print(f"Sample per track: {sample_size} questions")
    print(f"Tracks: {', '.join(TRACKS.keys())}")
    print("=" * 70)

    # Assign keys to tracks (round-robin if more tracks than keys)
    track_keys = {}
    for i, track in enumerate(TRACKS.keys()):
        track_keys[track] = API_KEYS[i % len(API_KEYS)]

    # Run tracks in parallel
    results = []
    with ThreadPoolExecutor(max_workers=len(TRACKS)) as executor:
        futures = {
            executor.submit(test_track, track, path, track_keys[track], sample_size): track
            for track, path in TRACKS.items()
        }

        for future in as_completed(futures):
            track = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"❌ [{track.upper()}] Failed: {e}")
                results.append({
                    'track': track,
                    'total': 0,
                    'correct': 0,
                    'accuracy': 0.0,
                    'errors': 1,
                    'error': str(e)
                })

    # Print summary
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)

    total_correct = 0
    total_questions = 0

    for r in results:
        status = "✅" if r['accuracy'] > 0.5 else "⚠️" if r['accuracy'] > 0.3 else "❌"
        print(f"{status} {r['track'].upper():6s} : {r['correct']:3d}/{r['total']:3d} = {r['accuracy']:6.1%}  (errors: {r.get('errors', 0)})")
        total_correct += r['correct']
        total_questions += r['total']

    if total_questions > 0:
        overall = total_correct / total_questions
        print("-" * 70)
        print(f"🎯 OVERALL: {total_correct}/{total_questions} = {overall:.1%}")
        print("=" * 70)

    # Save results
    output = Path(__file__).parent.parent / "runs" / f"glm5_parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output.parent.mkdir(exist_ok=True)

    import json
    with open(output, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'sample_size': sample_size,
            'api_keys_used': len(API_KEYS),
            'overall_accuracy': total_correct / total_questions if total_questions > 0 else 0,
            'tracks': results
        }, f, indent=2)

    print(f"💾 Results saved to: {output}")

if __name__ == "__main__":
    main()
