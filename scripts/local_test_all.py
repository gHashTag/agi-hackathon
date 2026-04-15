#!/usr/bin/env python3
"""
Local test of all cleaned datasets with GLM-4-plus
Quick test: 10 questions per track
"""

import csv
import sys
import requests
from pathlib import Path

# Load API key
env_file = Path("/Users/playra/.claude/.env")
API_KEY = None
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.startswith("ZAI_KEY_1="):
                API_KEY = line.split("=", 1)[1].strip()
                break

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

DATASETS = {
    'THLP': 'kaggle/data/extra/thlp_mc_cleaned.csv',
    'TTM': 'kaggle/data/extra/ttm_mc_adversarial_v3.csv',
    'TAGP': 'kaggle/data/tagp_mc_cleaned.csv',
    'TEFB': 'kaggle/data/extra/tefb_mc_cleaned.csv',
    'TSCP': 'kaggle/data/extra/tscp_mc_cleaned.csv',
}

def load_questions(path, limit=10):
    questions = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('question_type', '').lower() == 'mc':
                questions.append(row)
                if len(questions) >= limit:
                    break
    return questions

def ask_glm(question):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""Answer with ONLY ONE letter (A, B, C, or D).

{question.get('question', '')}

{question.get('choices', '')}

Answer:"""

    payload = {
        "model": "glm-4-plus",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 10
    }

    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        result = r.json()
        if "choices" in result and result["choices"]:
            text = result["choices"][0]["message"]["content"].strip().upper()
            for letter in ['A', 'B', 'C', 'D']:
                if letter in text[:5]:
                    return letter
        return text[0] if text else 'A'
    except:
        return 'A'

def main():
    print("=" * 70)
    print("🧪 LOCAL TEST - ALL CLEANED DATASETS (10 Q each)")
    print("=" * 70)

    results = {}

    for track, path in DATASETS.items():
        print(f"\n{'─' * 70}")
        print(f"📋 {track}")
        print(f"{'─' * 70}")

        questions = load_questions(path, limit=10)
        print(f"Loaded: {len(questions)} questions")

        correct = 0
        for i, q in enumerate(questions, 1):
            predicted = ask_glm(q)
            expected = q.get('answer', '').upper()
            if predicted == expected:
                correct += 1
            icon = "✓" if predicted == expected else "✗"
            print(f"  {i}. {icon} P:{predicted} E:{expected}")

        accuracy = correct / len(questions) if questions else 0
        results[track] = {'correct': correct, 'total': len(questions), 'accuracy': accuracy}
        print(f"  → {correct}/{len(questions)} = {accuracy:.0%}")

    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)

    total_c = sum(r['correct'] for r in results.values())
    total_t = sum(r['total'] for r in results.values())

    for track, r in results.items():
        icon = "✅" if r['accuracy'] > 0.5 else "⚠️" if r['accuracy'] > 0.25 else "❌"
        print(f"{icon} {track}: {r['correct']}/{r['total']} = {r['accuracy']:.0%}")

    print("-" * 70)
    print(f"🎯 OVERALL: {total_c}/{total_t} = {total_c/total_t:.0%}")
    print("=" * 70)

if __name__ == "__main__":
    main()
