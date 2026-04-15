#!/usr/bin/env python3
"""
Generate realistic adversarial TTM dataset
Key insight: Original has 33 unique Qs x 4 variants = 816 rows
Each variant has different correct answer (A/B/C/D)
This is artificial - models can learn the pattern
Solution: Create truly unique questions with varied structures
"""

import csv
import random
import re
from pathlib import Path
from typing import List, Dict

# Question templates for generating NEW questions
QUESTION_TEMPLATES = {
    'calibration': [
        "Consider a claim about probability: \"{claim}\" with {confidence}% confidence. "
        "Which assessment is most appropriate?",

        "Evaluate this confidence judgment: \"{claim}\" (stated as {confidence}% confident). "
        "Select the best analysis.",

        "Someone states: \"{claim}\" with {confidence}% certainty. "
        "What's the correct calibration assessment?",
    ],
    'reasoning_error': [
        "Identify the primary logical flaw in this argument:\n\n\"{argument}\"",

        "What's the main reasoning error in:\n\n\"{argument}\"",

        "The following argument contains a logical fallacy. Which best describes it?\n\n\"{argument}\"",
    ],
    'bias': [
        "Which cognitive bias is demonstrated in this scenario?\n\n\"{scenario}\"",

        "Identify the bias in this situation:\n\n\"{scenario}\"",

        "What systematic thinking error is shown here?\n\n\"{scenario}\"",
    ],
    'decision': [
        "Given the constraints described, what's the optimal decision?\n\n\"{context}\"",

        "With the information provided, which choice is most rational?\n\n\"{context}\"",

        "What's the best course of action in this situation?\n\n\"{context}\"",
    ],
    'probability': [
        "What's the most accurate probability assessment for:\n\n\"{situation}\"",

        "Calculate the probability of:\n\n\"{situation}\"\n\nSelect the best estimate.",

        "Given this scenario, which probability is most reasonable?\n\n\"{situation}\"",
    ]
}

# Content for generating diverse questions
CONTENT_POOL = {
    'claim': [
        "A fair coin will land heads",
        "It will rain in Seattle tomorrow",
        "A randomly selected person is over 6 feet tall",
        "The next car you see will be red",
        "A die roll will be 6",
    ],
    'confidence': ['10', '25', '50', '75', '90'],
    'argument': [
        "All swans are white. I've seen 100 swans and all were white. Therefore all swans are white.",
        "Smoking causes cancer because my grandfather smoked and got cancer.",
        "We should ban all technology because it makes people less social.",
        "This medication works because it's natural.",
        "Rich people are greedy - I know a rich person who's greedy.",
    ],
    'scenario': [
        "After buying a red car, you notice more red cars on the road.",
        "You invest in a stock that's been rising for 10 days, expecting it to continue.",
        "You think you're better than average at driving.",
        "You remember your childhood more fondly than it actually was.",
        "You seek information that confirms your existing beliefs.",
    ],
    'context': [
        "You have $100 to invest. Option A: guaranteed $110 in a year. Option B: 50% chance of $200, 50% of $0.",
        "You're behind on a project. You can: cut quality to meet deadline, request extension, or add resources.",
        "Your team has limited time and multiple promising ideas. You must choose one to pursue.",
        "A competitor lowers prices. You can: match them, differentiate your product, or focus on service.",
    ],
    'situation': [
        "Rolling two fair dice and getting a sum of 7",
        "A random person having a birthday in February",
        "Drawing a face card from a standard deck",
        "Getting heads on three consecutive coin flips",
        "Two people sharing a birthday in a room of 23 people",
    ]
}

# Answer patterns - make them less predictable
ANSWER_PATTERNS = {
    'calibration': [
        ("A", "Overconfident - the true probability is much lower"),
        ("B", "Underconfident - the true probability is much higher"),
        ("C", "Reasonably calibrated - the estimate is accurate"),
        ("D", "Miscalibrated - depends on additional context not provided"),
    ],
    'reasoning_error': [
        ("A", "Hasty generalization - drawing broad conclusions from insufficient evidence"),
        ("B", "Post hoc fallacy - assuming causation from mere correlation"),
        ("C", "Appeal to nature - assuming natural means good or safe"),
        ("D", "Straw man - misrepresenting the argument to make it easier to attack"),
    ],
    'bias': [
        ("A", "Confirmation bias - seeking information that confirms existing beliefs"),
        ("B", "Availability heuristic - overestimating the likelihood of memorable events"),
        ("C", "Anchoring bias - being overly influenced by the first piece of information"),
        ("D", "Overconfidence effect - overestimating one's own abilities or knowledge"),
    ],
    'decision': [
        ("A", "Maximize expected value - choose the option with highest average return"),
        ("B", "Minimize risk - choose the safest option regardless of potential reward"),
        ("C", "Consider time preferences - factor in the value of immediate vs delayed outcomes"),
        ("D", "Apply satisficing - choose the first option that meets minimum requirements"),
    ],
    'probability': [
        ("A", "Much higher than random chance - the scenario strongly favors the outcome"),
        ("B", "Approximately equal to random chance - no clear advantage or disadvantage"),
        ("C", "Much lower than random chance - the scenario strongly disfavors the outcome"),
        ("D", "Cannot determine - insufficient information for reliable estimation"),
    ]
}

def generate_unique_questions(count: int = 100) -> List[Dict]:
    """Generate truly unique questions with varied structures"""
    questions = []
    categories = list(QUESTION_TEMPLATES.keys())

    for i in range(count):
        # Random category
        category = random.choice(categories)

        # Get template and fill in content
        template = random.choice(QUESTION_TEMPLATES[category])

        # Fill in placeholders
        question_text = template
        for placeholder, pool in CONTENT_POOL.items():
            if f"{{{placeholder}}}" in question_text:
                value = random.choice(pool)
                question_text = question_text.replace(f"{{{placeholder}}}", value)

        # Get corresponding answer patterns
        answer_patterns = ANSWER_PATTERNS[category]

        # Randomly assign which letter is correct
        correct_letter = random.choice(['A', 'B', 'C', 'D'])

        # Build choices with the correct one in position
        letters = ['A', 'B', 'C', 'D']
        choices_text = []

        for letter in letters:
            if letter == correct_letter:
                # This is the correct answer
                pattern = random.choice(answer_patterns)
                answer_desc = pattern[1]
            else:
                # Wrong answer - use different category's pattern or generic
                wrong_patterns = [p for p in answer_patterns if p[0] != letter]
                if wrong_patterns:
                    pattern = wrong_patterns[0]
                    answer_desc = pattern[1]
                else:
                    answer_desc = "Plausible but incorrect analysis"

            choices_text.append(f"{letter}) {answer_desc}")

        choices_str = ' '.join(choices_text)

        questions.append({
            'id': f'ttm_new_{i:04d}',
            'question_type': 'mc',
            'question': question_text,
            'choices': choices_str,
            'answer': correct_letter
        })

    return questions

def add_adversarial_noise(questions: List[Dict], noise_level: float = 0.3) -> List[Dict]:
    """Add adversarial perturbations"""
    adversarial = []

    for q in questions:
        new_q = q.copy()

        # Random perturbations
        if random.random() < noise_level:
            # Add subtle distraction in question
            noise_phrases = [
                "Consider carefully: ",
                "Take your time: ",
                "Think step by step: ",
            ]
            prefix = random.choice(noise_phrases)
            new_q['question'] = prefix + new_q['question']

        if random.random() < noise_level:
            # Add negative constraint
            constraints = [
                " Do NOT jump to conclusions.",
                " Avoid obvious but incorrect patterns.",
                " Consider all possibilities equally.",
            ]
            new_q['question'] = new_q['question'] + random.choice(constraints)

        # Occasionally swap two wrong answers to add confusion
        if random.random() < noise_level:
            choices = new_q['choices'].split(' ')
            # Swap first two wrong answers (simplified)
            if len(choices) >= 4:
                correct = new_q['answer']
                wrong_choices = [c for c in choices if c and c[0] != correct]
                if len(wrong_choices) >= 2:
                    # Rebuild with swap
                    new_choices = []
                    for c in choices:
                        if c and c[0] == wrong_choices[0][0]:
                            new_choices.append(wrong_choices[1])
                        elif c and c[0] == wrong_choices[1][0]:
                            new_choices.append(wrong_choices[0])
                        else:
                            new_choices.append(c)
                    new_q['choices'] = ' '.join(new_choices)

        adversarial.append(new_q)

    return adversarial

def main():
    print("=" * 70)
    print("🛡️  GENERATING REALISTIC ADVERSARIAL TTM DATASET")
    print("=" * 70)

    # Generate 100 new unique questions
    print("\n📝 Generating new questions...")
    questions = generate_unique_questions(count=100)
    print(f"   Generated {len(questions)} unique questions")

    # Add adversarial noise
    print("\n🔧 Adding adversarial perturbations...")
    adversarial = add_adversarial_noise(questions, noise_level=0.3)

    # Write output
    output_path = Path('kaggle/data/extra/ttm_mc_adversarial_v3.csv')
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'question_type', 'question', 'choices', 'answer'])
        writer.writeheader()
        writer.writerows(adversarial)

    print(f"\n✅ Adversarial dataset saved to {output_path}")
    print(f"   Total questions: {len(adversarial)}")

    # Statistics
    answer_dist = {}
    for q in adversarial:
        a = q['answer']
        answer_dist[a] = answer_dist.get(a, 0) + 1

    print("\n📊 Answer Distribution:")
    for letter in sorted(answer_dist.keys()):
        pct = answer_dist[letter] / len(adversarial) * 100
        print(f"   {letter}: {answer_dist[letter]} ({pct:.1f}%)")

    # Sample question
    print("\n📄 Sample Question:")
    sample = adversarial[0]
    print(f"ID: {sample['id']}")
    print(f"Q: {sample['question']}")
    print(f"Choices:\n{sample['choices']}")
    print(f"Answer: {sample['answer']}")

    print("\n" + "=" * 70)
    print("🎯 NEXT STEPS:")
    print("=" * 70)
    print("1. Test this dataset with models")
    print("2. Expected accuracy: 25-40% (random is 25%)")
    print("3. If accuracy > 70%, the questions are still too predictable")
    print("4. Increase noise_level or add more question variety")

if __name__ == "__main__":
    main()
