#!/usr/bin/env python3
"""
Quick test script for GLM-5 with full dataset format
"""

import csv
import os
import sys
import requests
from pathlib import Path
from datetime import datetime

# Load API key
env_file = Path("/Users/playra/.claude/.env")
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.startswith("ZAI_KEY_1="):
                API_KEY = line.split("=", 1)[1].strip()
                break
else:
    print("Error: .env file not found")
    sys.exit(1)

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def load_questions(csv_path, sample_size=10):
    """Load questions from CSV"""
    questions = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('question_type') == 'mc':
                questions.append(row)
                if len(questions) >= sample_size:
                    break
    return questions

def evaluate_glm5(question):
    """Evaluate single question with GLM-5"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Parse choices from the "choices" field (format: A) ... B) ... C) ... D) ...)
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
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        answer = result["choices"][0]["message"]["content"].strip().upper()
        # Extract just the letter
        for letter in ['A', 'B', 'C', 'D']:
            if letter in answer[:5]:
                return letter
        return answer[0] if answer else 'A'
    except Exception as e:
        print(f"Error: {e}")
        return 'A'

def main():
    csv_path = Path(__file__).parent.parent / "kaggle" / "data" / "extra" / "thlp_mc_new.csv"

    if not csv_path.exists():
        print(f"Error: {csv_path} not found")
        sys.exit(1)

    print("=" * 60)
    print("Testing GLM-5 on THLP dataset")
    print("=" * 60)

    questions = load_questions(csv_path, sample_size=10)
    print(f"Loaded {len(questions)} questions\n")

    correct = 0
    total = 0

    for i, q in enumerate(questions, 1):
        predicted = evaluate_glm5(q)
        expected = q.get('answer', '').upper()
        is_correct = predicted == expected

        if is_correct:
            correct += 1
            status = "✓"
        else:
            status = "✗"

        print(f"{i}. {status} Predicted: {predicted}, Expected: {expected}, Type: {q.get('question_type', 'N/A')}")
        total += 1

    accuracy = correct / total if total > 0 else 0
    print("\n" + "=" * 60)
    print(f"Results: {correct}/{total} correct")
    print(f"Accuracy: {accuracy:.2%}")
    print("=" * 60)

if __name__ == "__main__":
    main()
