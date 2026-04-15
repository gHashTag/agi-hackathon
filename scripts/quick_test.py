#!/usr/bin/env python3
"""
Quick test: 5 questions per track to verify functionality
"""

import csv
import sys
import requests
from pathlib import Path
from typing import List, Dict, Tuple

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

TRACKS = {
    'THLP': 'kaggle/data/extra/thlp_mc_new.csv',
    'TTM': 'kaggle/data/extra/ttm_mc_new.csv',
    'TAGP': 'kaggle/data/tagp_mc.csv',
    'TEFB': 'kaggle/data/extra/tefb_mc_new.csv',
    'TSCP': 'kaggle/data/extra/tscp_mc_new.csv'
}

def load_questions(csv_path: str, limit: int = 5) -> List[Dict]:
    """Load MC questions from CSV"""
    questions = []
    path = Path(csv_path)
    if not path.exists():
        print(f"⚠️  {csv_path} not found")
        return []

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('question_type', '').lower() == 'mc':
                questions.append(row)
                if len(questions) >= limit:
                    break
    return questions

def ask_glm(question: Dict) -> Tuple[str, str]:
    """Ask GLM-5 a question, returns (answer, status)"""
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
                    return letter, "OK"
            return text[0] if text else 'A', "OK"
        return 'A', "No response"

    except Exception as e:
        return 'A', f"Error: {str(e)[:30]}"

def main():
    print("=" * 60)
    print("🚀 QUICK FUNCTIONALITY TEST - 5 QUESTIONS PER TRACK")
    print("=" * 60)

    all_results = []

    for track_name, csv_path in TRACKS.items():
        print(f"\n{'─' * 60}")
        print(f"📋 {track_name}")
        print(f"{'─' * 60}")

        questions = load_questions(csv_path, limit=5)

        if not questions:
            print(f"❌ No questions loaded")
            continue

        print(f"Loaded {len(questions)} questions")

        correct = 0
        for i, q in enumerate(questions, 1):
            predicted, status = ask_glm(q)
            expected = q.get('answer', '').upper()
            is_correct = predicted == expected

            if is_correct:
                correct += 1
                icon = "✓"
            else:
                icon = "✗"

            print(f"  {i}. {icon} P:{predicted} E:{expected} [{status}]")

        accuracy = correct / len(questions) if questions else 0
        print(f"  → {correct}/{len(questions)} = {accuracy:.0%}")

        all_results.append({
            'track': track_name,
            'correct': correct,
            'total': len(questions),
            'accuracy': accuracy
        })

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    total_correct = sum(r['correct'] for r in all_results)
    total_questions = sum(r['total'] for r in all_results)

    for r in all_results:
        icon = "✅" if r['accuracy'] >= 0.6 else "⚠️" if r['accuracy'] >= 0.4 else "❌"
        print(f"{icon} {r['track']:6s} : {r['correct']}/{r['total']} = {r['accuracy']:.0%}")

    print("-" * 60)
    if total_questions > 0:
        overall = total_correct / total_questions
        print(f"🎯 OVERALL: {total_correct}/{total_questions} = {overall:.0%}")
    print("=" * 60)

    print("\n✅ Functionality test complete!")
    print("Ready for: Kaggle notebooks upload & full evaluation")

if __name__ == "__main__":
    main()
