#!/usr/bin/env python3
"""
Adversarial generators for TTM and TSCP (English versions)

Based on Big-Bench and ARC principles:
- Multi-step reasoning
- Adversarial examples
"""

import csv
import random
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Common templates for both tracks
COMMON_TEMPLATES = [
    {
        "question": "In {domain} field, method {method_a} works well but is computationally expensive. Method {method_b} is faster but has {flaw}. You have limited budget. What's your BEST decision? {adversarial_hint} Consider computational cost vs. accuracy requirements vs. budget constraints.",
        "choices": [
            "A) Use {method_a} - prioritize accuracy within budget",
            "B) Use {method_b} - faster results, accept lower accuracy",
            "C) Hybrid approach - use {method_b} with {method_a} for verification",
            "D) Use {method_a} - defer to future budget (save for hybrid)"
        ],
        "answer": 1,  # Index 1 (cost-benefit analysis)
        "difficulty": "medium",
        "explanation": "Tests strategic decision-making under constraints - a key TTM/TSCP skill.",
        "domain": "mixed"
    }
]

# TTM-specific templates (from original script, English)
TTM_TEMPLATES = {
    "trinity_identity": [
        {
            "question": "Trinity Identity: φ² + φ⁻² = 3, where φ = (1+√5)/2 is the golden ratio. What's the exact value of φ⁴ + φ⁻⁴?",
            "choices": [
                "A) 5",
                "B) 7",
                "C) 9",
                "D) 11"
            ],
            "answer": 0,  # φ⁴ + φ⁻⁴ = 3
            "difficulty": "easy",
            "explanation": "Tests understanding of Trinity Identity - key TTM concept."
        },
        {
            "question": "In VS (Vector Symbolic Architecture), neural networks often use {n}-dimensional spaces. For {target_dim}-dimensional VSA, matrix multiplication complexity is O(n³). However, the Toffoli {toffoli} tensor train algorithm reduces this to O(n² log n) for {target_dim}≥1000. What's the BIG-O complexity improvement factor of Toffoli vs. naive matmul? {adversarial_hint} Express Toffoli complexity as O(n² log n) / O(n³).",
            "choices": [
                "A) O(n² log n) / O(n³)",
                "B) O(n³)",
                "C) O(n³ log n)",
                "D) Exponential - O(n^3)"
            ],
            "answer": 0,  # Toffoli O(n² log n)
            "difficulty": "medium",
            "explanation": "Tests understanding of computational complexity - key TTM/TSCP skill."
        },
        {
            "question": "In vector encoding, if you encode two orthogonal vectors {v1} and {v2} using separate encoding, the similarity is cos(v1, v2) = 0. However, in some frameworks, concatenation encoding is used, where similarity is v1 + v2. How does this affect BIG-O complexity? {adversarial_hint} Consider concatenation cost vs. dimensionality reduction.",
            "choices": [
                "A) Same BIG-O (O(n²)) - similarity 0",
                "B) Concatenation (O(n)) - similarity v1 + v2",
                "C) Separate (O(n)) - similarity 0, but higher dimensionality"
            ],
            "answer": 1,  # Concatenation (O(n))
            "difficulty": "medium",
            "explanation": "Tests understanding of encoding strategies and their complexity implications - key TTM/TSCP skill."
        },
        {
            "question": "E8 Lie group has dimension 248. The Coxeter number h∨ is {value}. In {basis}, the dual Coxeter number is 24 - h∨. What's the value of h∨²? {adversarial_hint} Consider the properties of Coxeter numbers: h∨² = h∨ × h∨, h∨⁶² = (h∨')^4.",
            "choices": [
                "A) 24 - h∨ × h∨",
                "B) 12 - h∨",
                "C) 6 - h∨",
                "D) 2 - h∨²"
            ],
            "answer": 0,  # 24 - h∨ × h∨
            "difficulty": "medium",
            "explanation": "Tests understanding of E8 group theory - Coxeter numbers properties."
        },
        {
            "question": "In {basis}, the mass spectrum is given by m_i = 2M sin(πi/(h+1)), where h = h∨ is the Coxeter number from the dual Coxeter number. This formula appears in various quantum corrections. For {target_mass} < h, what is the value of m_{target_mass}? {adversarial_hint} Use the formula structure and identify the key parameter.",
            "choices": [
                "A) m_{target_mass} - M sin(πi/(h+1))",
                "B) 2M sin(πi/(h+1))",
                "C) 4M sin(πi/(h+1))"
            ],
            "answer": 0,  # Use Koide formula structure
            "difficulty": "medium",
            "explanation": "Tests understanding of the Koide formula for lepton masses - a key TTM/TSCP skill."
        },
        {
            "question": "The fine structure constant α ≈ 1/137.036. If we consider α ≈ 4π³/φ⁸, what is the approximate value of φ⁸? {adversarial_hint} Use φ ≈ 1.618 to calculate 4φ³/φ⁸ ≈ 4 × 4.236 = 16.944, then divide by φ² ≈ 2.618.",
            "choices": [
                "A) 16.94",
                "B) 16.94",
                "C) 16.94",
                "D) 16.94"
            ],
            "answer": 0,  # All approximately 16.94
            "difficulty": "medium",
            "explanation": "Tests understanding of fine structure constant approximations and golden ratio relationships."
        }
    ]
}

# Adversarial techniques
ADVERSARIAL_TECHNIQUES = [
    # Complexity manipulation
    "reduce_complexity",
    "increase_specificity",

    # Domain shift
    "change_domain",

    # Negative constraints
    "add_negative_constraints",

    # Choice scrambling
    "scramble_choices",

    # Distractor enhancement
    "enhance_distractors",

    # Context shift
    "shift_context",

    # Paraphrasing (already in original templates)
    "paraphrase_questions"
]

class UnifiedAdversarialGenerator:
    def __init__(self, config: Dict):
        self.config = config
        self.templates = COMMON_TEMPLATES
        self.num_questions = config.get('num_questions', 100)
        self.random = random.Random(config.get('seed', 42))

    def generate_questions(self, tracks: List[str]) -> List[Dict]:
        """Generate adversarial TTM and TSCP questions"""
        all_questions = []

        for track in tracks:
            if track not in ['ttm', 'tscp']:
                continue

            # Get templates for this track
            if track == 'ttm':
                templates = self.templates.get('ttm_templates', COMMON_TEMPLATES)
            elif track == 'tscp':
                templates = self.templates.get('tscp_templates', COMMON_TEMPLATES)
            else:
                continue

            # Determine number of questions per track
            num_per_track = self.num_questions // len(tracks)

            for i in range(num_per_track):
                # Select random template
                template = self.random.choice(templates)

                # Generate question with randomized parameters
                q = self.generate_question(template)
                all_questions.append(q)

        return all_questions

    def generate_question(self, template: Dict) -> Dict:
        """Generate a single adversarial question from template"""
        # Get base question
        base_q = template['question']
        base_choices = template['choices']

        # Apply adversarial transformations based on technique
        techique = template.get('technique', '')

        # Determine correct answer index
        correct_idx = template['answer'] - 1  # Convert to 0-index

        # Apply transformations based on technique
        if techique == 'reduce_complexity':
            # Reduce complexity by changing parameters
            if 'dimension' in base_q.lower():
                # Change large dimension to small
                base_q = base_q.replace('{target_dim}', str(int(base_choices[0].get('dimension', 1000) // 10))
                base_q = base_q.replace('{basis}', str(int(base_choices[0].get('basis', 'R')))
            if 'value' in base_q.lower():
                base_q = base_q.replace('{value}', str(int(base_choices[0].get('value', 1000) // 10))
        elif techique == 'increase_specificity':
            # Make more specific
            if 'orthogonal' in base_q.lower():
                # Add specific context
                base_q = base_q.replace('{v1}', '{v1} and {v2}')
            if 'linear' in base_q.lower():
                # Make linear
                base_q = base_q.replace('O(n)', 'O(n²)')
        elif techique == 'change_domain':
            # Change to different domain
            base_q = base_q.replace('vector encoding', 'matrix multiplication')
        elif techique == 'add_negative_constraints':
            # Add constraint that makes solution invalid
            base_q = base_q + " However, {random.choice(['', 'cannot', 'invalid'])} is not possible."
        elif techique == 'scramble_choices':
            # P0.7: Scramble choices
            original_choices = template['choices']

            # Rotate
            rotated = original_choices[1:] + original_choices[:1]

            # Reverse some
            if len(original_choices) == 4:
                rotated[2], rotated[3] = rotated[3], rotated[2]

            # Shuffle
            random.shuffle(rotated)

            q_text = base_q.replace('{thought_hint}', '{thought_hint}')
            template['choices'] = rotated

        elif techique == 'enhance_distractors':
            # P0.4: Enhance distractors
            original_choices = template['choices']

            for i, choice in enumerate(original_choices):
                if choice == template['answer']:
                    continue  # Don't change correct answer

                # Technique 1: Add "in most cases"
                if 'A) ' in choice:
                    choice = choice.replace('A) ', 'A) (in most cases)')
                elif 'B) ' in choice:
                    choice = choice.replace('B) ', 'B) (in most cases)')
                elif 'C) ' in choice:
                    choice = choice.replace('C) ', 'C) (in most cases)')

                # Technique 2: Add "generally"
                if 'generally' in choice.lower():
                    choice = choice.replace('generally', 'generally speaking')

            new_choices = []
            for choice in original_choices:
                if choice != template['answer']:
                    new_choices.append(choice)

            template['choices'] = new_choices

        elif techique == 'shift_context':
            # P0.5: Shift temporal/spatial framing
            q_text = base_q

            # Technique 1: Change time references
            if 'tomorrow' in q_text.lower():
                q_text = q_text.replace('tomorrow', 'next week')
            elif 'yesterday' in q_text.lower():
                q_text = q_text.replace('yesterday', 'last week')
            elif 'last year' in q_text.lower():
                q_text = q_text.replace('last year', 'previous cycle')

            # Technique 2: Shift quantities
            if '100%' in q_text:
                q_text = q_text.replace('100%', '99.9%')
            if '50%' in q_text:
                q_text = q_text.replace('50%', '50.1%')

            # Add shift hint
            q_text = q_text.replace('{thought_hint}', '{thought_hint}')

            # Re-generate choices
            template['choices'] = template['choices']

        elif techique == 'paraphrase_questions':
            # P0.1: Paraphrasing (already in original templates)
            q_text = base_q

        else:
            # No transformation - use as-is
            q_text = base_q

        question = {
            **q
        }
        all_questions.append(question)

        return all_questions

    def save_questions(self, questions: List[Dict], output_path: str):
        """Save adversarial TTM/TSCP questions to CSV"""
        fieldnames = ['question_type', 'question', 'choices', 'answer', 'difficulty', 'explanation', 'domain']

        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(fieldnames)

            for q in questions:
                row = [
                    'mc',
                    q.get('domain') or 'mixed',
                    q['question'],
                    '|'.join(q['choices']),
                    q['answer'],
                    q['difficulty'],
                    q['explanation']
                ]
                writer.writerow(row)

def main():
    """Main execution function"""
    # Configuration
    config = {
        'num_questions': 100,
        'seed': 42,
        'tracks': ['ttm', 'tscp']
    }

    generator = UnifiedAdversarialGenerator(config)

    # Parse command line arguments
    import sys
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        config['num_questions'] = num_questions
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42

    # Generate questions
    questions = generator.generate_questions(config['tracks'])

    # Save
    output_path = '/Users/playra/agi-hackathon/kaggle/data/extra/ttm_mc_adversarial_en.csv'
    generator.save_questions(questions, output_path)

    print(f"✅ Generated {len(questions)} adversarial TTM/TSCP questions")
    print(f"   Saved to: {output_path}")

if __name__ == '__main__':
    main()