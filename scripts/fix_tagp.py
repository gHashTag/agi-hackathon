#!/usr/bin/env python3
"""
Quick fix for TAGP - remove duplicates and create adversarial version
"""

import csv
import random
import re
from pathlib import Path

# Load TAGP
path = 'kaggle/data/tagp_mc.csv'
questions = []

with open(path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get('question_type', '').lower() == 'mc':
            questions.append(row)

print(f"Loaded {len(questions)} questions")

# Remove duplicates (by question text)
seen = {}
unique = []
for q in questions:
    text = re.sub(r'\s+', ' ', q.get('question', '').lower().strip())
    h = hash(text)
    if h not in seen:
        seen[h] = True
        unique.append(q)

print(f"Removed {len(questions) - len(unique)} duplicates")
print(f"Unique: {len(unique)}")

# Create adversarial version with perturbations
adversarial = []

# Noise patterns
noise_prefixes = [
    "Consider carefully: ",
    "Think step by step: ",
    "Analyze logically: ",
]

noise_suffixes = [
    " Do NOT assume without evidence.",
    " Avoid jumping to conclusions.",
    " Consider all possibilities.",
]

for i, q in enumerate(unique):
    new_q = q.copy()
    question_text = new_q['question']

    # Apply noise randomly
    if random.random() < 0.4:
        if random.random() < 0.5:
            question_text = random.choice(noise_prefixes) + question_text
        else:
            question_text = question_text + random.choice(noise_suffixes)

    new_q['question'] = question_text
    new_q['id'] = f'tagp_adv_{i:04d}'

    adversarial.append(new_q)

# Save adversarial
output = 'kaggle/data/tagp_mc_adversarial.csv'
with open(output, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'question_type', 'question', 'choices', 'answer'])
    writer.writeheader()
    writer.writerows(adversarial)

print(f"\n✅ Saved {len(adversarial)} adversarial questions to {output}")

# Statistics
answer_dist = {}
for q in adversarial:
    a = q.get('answer', '').upper()
    answer_dist[a] = answer_dist.get(a, 0) + 1

print(f"\n📊 Answer distribution:")
for letter in sorted(answer_dist.keys()):
    pct = answer_dist[letter] / len(adversarial) * 100
    print(f"   {letter}: {answer_dist[letter]} ({pct:.1f}%)")
