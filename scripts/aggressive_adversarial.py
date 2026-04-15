#!/usr/bin/env python3
"""
Create MORE aggressive adversarial versions for THLP and TAGP
"""

import csv
import random
from pathlib import Path

def aggressive_paraphrase(text):
    """More aggressive paraphrasing"""
    replacements = [
        ("What is", "Determine the value of"),
        ("Which", "Select the option that represents"),
        ("The best", "The most accurate"),
        ("correct", "appropriate"),
        ("Choose", "Identify"),
        ("answer", "response"),
    ]

    result = text
    for old, new in replacements:
        if random.random() < 0.4:
            result = result.replace(old, new)

    # Add misleading context
    contexts = [
        " Note: Multiple options may appear plausible.",
        " Careful: This requires precise reasoning.",
        " Consider: Common misconceptions may lead to wrong answers.",
        " Analyze: Surface-level reading may be misleading.",
    ]

    if random.random() < 0.5:
        result = result + random.choice(contexts)

    return result

def scramble_choices(choices, correct):
    """Scramble and modify choices"""
    parts = choices.split(')')
    if len(parts) < 4:
        return choices

    # Extract choices
    choice_list = []
    for part in parts[1:5]:  # Skip first empty part
        if part.strip():
            letter = part.strip()[0]
            text = part.strip()[1:].strip()
            choice_list.append((letter, text))

    # Scramble order
    random.shuffle(choice_list)

    # Rebuild with new letters
    new_letters = ['A', 'B', 'C', 'D']
    new_choices = []
    new_correct = None

    for (old_letter, text), new_letter in zip(choice_list, new_letters):
        new_choices.append(f"{new_letter}) {text}")
        if old_letter == correct:
            new_correct = new_letter

    return ' '.join(new_choices), new_correct

def process_dataset(input_path, output_path):
    """Process a dataset with aggressive adversarial"""
    questions = []

    with open(input_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('question_type', '').lower() == 'mc':
                questions.append(row)

    print(f"Loaded {len(questions)} questions")

    adversarial = []
    for i, q in enumerate(questions):
        new_q = q.copy()

        # Aggressive paraphrase
        new_q['question'] = aggressive_paraphrase(q['question'])

        # Scramble choices
        original_correct = q.get('answer', '').upper()
        new_choices, new_correct = scramble_choices(q.get('choices', ''), original_correct)

        new_q['choices'] = new_choices
        new_q['answer'] = new_correct
        new_q['id'] = f"adv_{i:04d}"

        adversarial.append(new_q)

    # Save
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'question_type', 'question', 'choices', 'answer'])
        writer.writeheader()
        writer.writerows(adversarial)

    print(f"✅ Saved {len(adversarial)} to {output_path}")

    return adversarial

# Process THLP
print("=" * 60)
print("THLP AGGRESSIVE ADVERSARIAL")
print("=" * 60)
process_dataset(
    'kaggle/data/extra/thlp_mc_cleaned.csv',
    'kaggle/data/extra/thlp_mc_aggressive.csv'
)

# Process TAGP
print("\n" + "=" * 60)
print("TAGP AGGRESSIVE ADVERSARIAL")
print("=" * 60)
process_dataset(
    'kaggle/data/tagp_mc_adversarial.csv',
    'kaggle/data/tagp_mc_aggressive.csv'
)

print("\n" + "=" * 60)
print("✅ AGGRESSIVE ADVERSARIAL VERSIONS CREATED")
print("=" * 60)
print("\nNow test with: python3 scripts/rapid_validation.py")
print("(Update DATASETS paths in the script)")
