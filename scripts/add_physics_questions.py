#!/usr/bin/env python3
"""
Convert JSON physics questions to CSV and append to TTM dataset
"""

import json
import csv
from pathlib import Path

# Load generated questions
with open('physics_golden_ratio_questions.json') as f:
    data = json.load(f)

questions = data['questions']

# Convert to CSV format
output_rows = []
for i, q in enumerate(questions, 1):
    output_rows.append({
        'id': f'ttm_physics_{i:04d}',
        'question_type': 'mc',
        'question': q['question'],
        'choices': q['choices'],
        'answer': q['answer']
    })

# Save to new file
output_path = 'kaggle/data/extra/ttm_physics_mc.csv'
with open(output_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'question_type', 'question', 'choices', 'answer'])
    writer.writeheader()
    writer.writerows(output_rows)

print(f"✅ Saved {len(output_rows)} physics questions to {output_path}")

# Also append to adversarial dataset
adversarial_path = 'kaggle/data/extra/ttm_mc_adversarial_v3.csv'

# Read existing
existing = []
with open(adversarial_path) as f:
    reader = csv.DictReader(f)
    existing = list(reader)

# Combine and save
combined = existing + output_rows
with open(adversarial_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'question_type', 'question', 'choices', 'answer'])
    writer.writeheader()
    writer.writerows(combined)

print(f"✅ Appended to {adversarial_path}")
print(f"   Total: {len(combined)} questions")

# Statistics
answer_dist = {}
for q in combined:
    a = q['answer']
    answer_dist[a] = answer_dist.get(a, 0) + 1

print(f"\n📊 Answer distribution:")
for letter in sorted(answer_dist.keys()):
    pct = answer_dist[letter] / len(combined) * 100
    print(f"   {letter}: {answer_dist[letter]} ({pct:.1f}%)")
