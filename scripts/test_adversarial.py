#!/usr/bin/env python3
"""
Test adversarial TTM dataset with GLM-5
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

if not API_KEY:
    print("❌ API key not found")
    sys.exit(1)

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def load_questions(csv_path):
    questions = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('question_type') == 'mc':
                questions.append(row)
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
        r = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        result = r.json()

        if "choices" in result and result["choices"]:
            text = result["choices"][0]["message"]["content"].strip().upper()
            for letter in ['A', 'B', 'C', 'D']:
                if letter in text[:5]:
                    return letter
            return text[0] if text else 'A'
        return 'A'
    except Exception as e:
        print(f"  Error: {str(e)[:30]}")
        return 'A'

def main():
    print("=" * 70)
    print("🧪 TESTING ADVERSARIAL TTM DATASET")
    print("=" * 70)

    csv_path = 'kaggle/data/extra/ttm_mc_adversarial_v3.csv'
    questions = load_questions(csv_path)

    print(f"\n📊 Loaded {len(questions)} questions")

    # Test first 20 to avoid rate limit
    test_count = 20
    print(f"🧪 Testing first {test_count} questions...\n")

    correct = 0
    results = []

    for i, q in enumerate(questions[:test_count], 1):
        predicted = ask_glm(q)
        expected = q.get('answer', '').upper()
        is_correct = predicted == expected

        if is_correct:
            correct += 1
            icon = "✓"
        else:
            icon = "✗"

        print(f"  {i:2d}. {icon} P:{predicted} E:{expected}")

        results.append({
            'id': q.get('id', ''),
            'predicted': predicted,
            'expected': expected,
            'correct': is_correct
        })

    accuracy = correct / test_count
    print("\n" + "-" * 70)
    print(f"📊 Result: {correct}/{test_count} = {accuracy:.1%}")
    print("-" * 70)

    # Interpretation
    print("\n🎯 INTERPRETATION:")
    if accuracy < 0.35:
        print(f"   ✅ {accuracy:.0%} is realistic - questions are truly challenging")
    elif accuracy < 0.60:
        print(f"   ⚠️  {accuracy:.0%} - moderate, could be better")
    elif accuracy < 0.80:
        print(f"   ⚠️  {accuracy:.0%} - still high, may need more perturbation")
    else:
        print(f"   🚨 {accuracy:.0%} - too high! Questions may still be predictable")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
