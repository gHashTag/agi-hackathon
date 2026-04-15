#!/usr/bin/env python3
"""
Generate adversarial versions of TTM dataset to mitigate data leakage
Applies perturbations: paraphrasing, negative constraints, distractor improvement
"""

import csv
import random
import re
from pathlib import Path
from typing import List, Dict

# Paraphrasing templates
PARAPHRASE_TEMPLATES = [
    # What is X -> What would X be / Which of these describes X / etc.
    (r"What is (\w+)", lambda m: f"Which of the following would {m.group(1)} be?"),
    (r"Which of the following (\w+)", lambda m: f"Select the option that best {m.group(1)}"),
    (r"Choose the correct", lambda m: "Identify the accurate"),
    (r"Select the best", lambda m: "Pick the most appropriate"),
    (r"The correct answer is", lambda m: "The accurate response represents"),
]

# Negative constraint phrases
NEGATIVE_CONSTRAINTS = [
    "Do NOT assume without evidence.",
    "Avoid common misconceptions.",
    "Consider all options carefully before choosing.",
    "Reject answers that make unwarranted assumptions.",
]

# Distractor enhancement patterns
DISTRACTOR_PATTERNS = {
    'A': ['common misconception', 'oversimplification', 'partial truth'],
    'B': ['inverse relationship', 'confused variable', 'wrong direction'],
    'C': ['irrelevant factor', 'unrelated concept', 'red herring'],
    'D': ['opposite conclusion', 'contradicted premise', 'invalid inference'],
}

def deduplicate_questions(questions: List[Dict]) -> List[Dict]:
    """Remove duplicate questions based on question text"""
    seen = set()
    unique = []

    for q in questions:
        # Normalize for comparison
        text = re.sub(r'\s+', ' ', q.get('question', '').lower().strip())
        h = hash(text)

        if h not in seen:
            seen.add(h)
            unique.append(q)

    print(f"🔧 Deduplication: {len(questions)} → {len(unique)} questions")
    return unique

def paraphrase_question(question: str) -> str:
    """Apply random paraphrasing to question"""
    for pattern, replacement in PARAPHRASE_TEMPLATES:
        if random.random() < 0.3:  # 30% chance to apply each template
            question = re.sub(pattern, replacement, question, flags=re.IGNORECASE)

    # Add negative constraint randomly
    if random.random() < 0.25:
        constraint = random.choice(NEGATIVE_CONSTRAINTS)
        question = f"{question} {constraint}"

    return question

def enhance_distractors(choices: str, correct_answer: str) -> str:
    """Enhance distractors to make them more plausible"""
    # Parse choices (format: A) ... B) ... C) ... D) ...)
    choices_list = re.split(r'(?=[ABCD]\))', choices)
    choices_list = [c.strip() for c in choices_list if c.strip()]

    # Enhance incorrect options
    enhanced = []
    for choice in choices_list:
        if choice and choice[0] != correct_answer:
            # Add plausibility to distractor
            if random.random() < 0.5:
                distractor_type = random.choice(DISTRACTOR_PATTERNS.get(choice[0], ['simplified']))
                choice = f"{choice} (This appears to be {distractor_type})"
        enhanced.append(choice)

    return ' '.join(enhanced)

def add_reasoning_requirement(question: str) -> str:
    """Add requirement for multi-step reasoning"""
    reasoning_prompts = [
        "This requires careful analysis of the logical structure.",
        "Apply critical thinking to avoid surface-level answers.",
        "Consider the chain of reasoning leading to each option.",
        "Evaluate the validity of each argument independently.",
    ]

    if random.random() < 0.4:
        prompt = random.choice(reasoning_prompts)
        question = f"{question} {prompt}"

    return question

def scramble_answer_order(q: Dict) -> Dict:
    """Scramble answer order to prevent pattern recognition"""
    # Parse current choices
    choices = q.get('choices', '')
    choice_list = re.split(r'(?=[ABCD]\))', choices)
    choice_list = [c.strip() for c in choice_list if c.strip()]

    # Extract the correct answer text
    correct_letter = q.get('answer', '').upper()

    # Find the correct choice text
    correct_text = None
    for choice in choice_list:
        if choice and choice[0] == correct_letter:
            correct_text = choice[2:].strip()  # Remove "A) " prefix
            break

    if not correct_text or len(choice_list) != 4:
        return q  # Can't scramble, return original

    # Scramble
    letters = ['A', 'B', 'C', 'D']
    texts = [c[2:].strip() for c in choice_list]

    # Find new position of correct answer
    shuffled = list(zip(letters, texts))
    random.shuffle(shuffled)

    # Find new correct letter
    new_letter = None
    for letter, text in shuffled:
        if text == correct_text:
            new_letter = letter
            break

    if not new_letter:
        return q

    # Rebuild choices
    new_choices = ' '.join([f"{l}) {t}" for l, t in shuffled])

    q['choices'] = new_choices
    q['answer'] = new_letter

    return q

def generate_adversarial_ttm(input_path: str, output_path: str, intensity: str = 'medium'):
    """
    Generate adversarial version of TTM dataset

    Args:
        input_path: Path to original TTM CSV
        output_path: Path for adversarial output
        intensity: 'light', 'medium', or 'heavy' - how aggressive perturbations to apply
    """
    intensity_levels = {
        'light': {'paraphrase': 0.2, 'reasoning': 0.3, 'scramble': 0.3},
        'medium': {'paraphrase': 0.5, 'reasoning': 0.5, 'scramble': 0.5},
        'heavy': {'paraphrase': 0.8, 'reasoning': 0.7, 'scramble': 0.7},
    }

    probs = intensity_levels.get(intensity, intensity_levels['medium'])

    # Load questions
    questions = []
    with open(input_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('question_type') == 'mc':
                questions.append(row)

    print(f"📊 Loaded {len(questions)} questions from {input_path}")

    # Deduplicate
    questions = deduplicate_questions(questions)

    # Apply perturbations
    adversarial = []
    stats = {
        'paraphrased': 0,
        'reasoning_added': 0,
        'scrambled': 0,
        'distractors_enhanced': 0,
    }

    for i, q in enumerate(questions, 1):
        new_q = q.copy()
        original_q = q.get('question', '')

        # Paraphrase
        if random.random() < probs['paraphrase']:
            new_q['question'] = paraphrase_question(original_q)
            stats['paraphrased'] += 1
        else:
            new_q['question'] = original_q

        # Add reasoning requirement
        if random.random() < probs['reasoning']:
            new_q['question'] = add_reasoning_requirement(new_q['question'])
            stats['reasoning_added'] += 1

        # Enhance distractors
        if random.random() < probs['paraphrase']:
            new_q['choices'] = enhance_distractors(q.get('choices', ''), q.get('answer', ''))
            stats['distractors_enhanced'] += 1
        else:
            new_q['choices'] = q.get('choices', '')

        # Scramble answer order
        if random.random() < probs['scramble']:
            new_q = scramble_answer_order(new_q)
            stats['scrambled'] += 1

        # Update ID to indicate adversarial version
        new_q['id'] = f"ADV_{q.get('id', i)}"

        adversarial.append(new_q)

        if i % 100 == 0:
            print(f"  Processed {i}/{len(questions)} questions...")

    # Write output
    output_file = Path(output_path)
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=adversarial[0].keys())
        writer.writeheader()
        writer.writerows(adversarial)

    print(f"\n✅ Adversarial dataset saved to {output_path}")
    print(f"   Total questions: {len(adversarial)}")

    print("\n📊 Perturbation Statistics:")
    print(f"   Paraphrased: {stats['paraphrased']} ({stats['paraphrased']/len(adversarial):.1%})")
    print(f"   Reasoning added: {stats['reasoning_added']} ({stats['reasoning_added']/len(adversarial):.1%})")
    print(f"   Distractors enhanced: {stats['distractors_enhanced']} ({stats['distractors_enhanced']/len(adversarial):.1%})")
    print(f"   Answers scrambled: {stats['scrambled']} ({stats['scrambled']/len(adversarial):.1%})")

    return adversarial

def main():
    print("=" * 70)
    print("🛡️  GENERATING ADVERSARIAL TTM DATASET")
    print("=" * 70)

    input_path = 'kaggle/data/extra/ttm_mc_new.csv'
    output_path = 'kaggle/data/extra/ttm_mc_adversarial_v2.csv'

    generate_adversarial_ttm(input_path, output_path, intensity='medium')

    print("\n" + "=" * 70)
    print("🎯 NEXT STEPS:")
    print("=" * 70)
    print("1. Test adversarial dataset with models")
    print("2. Verify accuracy drops significantly (should be < 70%)")
    print("3. If accuracy still high, increase intensity to 'heavy'")
    print("4. Apply similar process to other tracks if needed")

if __name__ == "__main__":
    main()
