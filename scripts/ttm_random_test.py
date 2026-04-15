#!/usr/bin/env python3
"""
Test 20 RANDOM questions from TTM to verify 100% wasn't luck
"""

import csv
import random
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

# Load all TTM questions
all_questions = []
with open('kaggle/data/extra/ttm_mc_new.csv') as f:
    reader = csv.DictReader(f)
    all_questions = [r for r in reader if r.get('question_type') == 'mc']

# Pick 20 random
test_questions = random.sample(all_questions, 20)

print("=" * 70)
print("🎲 TTM RANDOM TEST - 20 RANDOM QUESTIONS")
print("=" * 70)

correct = 0

for i, q in enumerate(test_questions, 1):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""Answer with ONLY ONE letter (A, B, C, or D).

{q.get('question', '')}

{q.get('choices', '')}

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
            predicted = 'A'
            for letter in ['A', 'B', 'C', 'D']:
                if letter in text[:5]:
                    predicted = letter
                    break

            expected = q.get('answer', '').upper()
            is_correct = predicted == expected

            if is_correct:
                correct += 1
                icon = "✓"
            else:
                icon = "✗"

            print(f"  {i:2d}. {icon} P:{predicted} E:{expected} ({q.get('id', '')})")
    except Exception as e:
        print(f"  {i:2d}. ✗ Error: {str(e)[:30]}")

accuracy = correct / 20
print("-" * 70)
print(f"📊 Result: {correct}/20 = {accuracy:.1%}")
print("=" * 70)

if accuracy == 1.0:
    print("\n🚨 WARNING: 100% on random questions suggests data leakage!")
elif accuracy > 0.8:
    print(f"\n⚠️  {accuracy:.0%} is still very high - suspicious")
else:
    print(f"\n✅ {accuracy:.0%} is more realistic")
