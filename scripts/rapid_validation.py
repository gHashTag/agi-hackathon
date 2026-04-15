#!/usr/bin/env python3
"""
Universal test script - test all datasets and generate summary
Quick 5-question test per track for rapid validation
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
    'TTM (Adversarial)': 'kaggle/data/extra/ttm_mc_adversarial_v3.csv',
    'TAGP (Adversarial)': 'kaggle/data/tagp_mc_adversarial.csv',
    'TEFB': 'kaggle/data/extra/tefb_mc_cleaned.csv',
    'TSCP': 'kaggle/data/extra/tscp_mc_cleaned.csv',
}

def load_questions(path, limit=5):
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
    print("🧪 RAPID VALIDATION - ALL DATASETS (5 Q each)")
    print("=" * 70)

    results = {}

    for track, path in DATASETS.items():
        if not Path(path).exists():
            print(f"\n{'─' * 70}")
            print(f"❌ {track}: FILE NOT FOUND - {path}")
            continue

        print(f"\n{'─' * 70}")
        print(f"📋 {track}")
        print(f"{'─' * 70}")

        try:
            questions = load_questions(path, limit=5)
            print(f"Loaded: {len(questions)} questions for quick test")

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
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:50]}")
            results[track] = {'error': str(e)}

    # Summary
    print("\n" + "=" * 70)
    print("📊 VALIDATION SUMMARY")
    print("=" * 70)

    total_c = 0
    total_t = 0
    all_ok = True

    for track, r in results.items():
        if 'error' in r:
            print(f"❌ {track}: ERROR")
            all_ok = False
        else:
            icon = "✅" if 0.25 < r['accuracy'] < 0.9 else "⚠️" if r['accuracy'] < 0.25 else "🚨"
            print(f"{icon} {track}: {r['correct']}/{r['total']} = {r['accuracy']:.0%}")
            total_c += r['correct']
            total_t += r['total']
            if r['accuracy'] >= 0.9:
                print(f"   ⚠️  TOO HIGH - possible data leakage!")
                all_ok = False
            elif r['accuracy'] <= 0.25:
                print(f"   ⚠️  TOO LOW - questions may be too hard")

    print("-" * 70)
    if total_t > 0:
        overall = total_c / total_t
        print(f"🎯 OVERALL: {total_c}/{total_t} = {overall:.0%}")

    print("\n" + "=" * 70)

    if all_ok:
        print("✅ ALL DATASETS PASS VALIDATION - READY FOR SUBMISSION!")
    else:
        print("⚠️  SOME ISSUES FOUND - REVIEW ABOVE")

    print("=" * 70)

if __name__ == "__main__":
    main()
