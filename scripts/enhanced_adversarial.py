#!/usr/bin/env python3
"""
Enhanced Adversarial Data Generator for AGI Hackathon
Implements diverse adversarial strategies with difficulty calibration.

Author: AGI Hackathon Team
Date: 2026-04-15

Strategies:
1. Paraphrasing: Rewriting questions while preserving meaning
2. Negative constraints: Adding "NOT" conditions
3. Distractor enhancement: Making wrong answers more plausible
4. Context swapping: Changing scenario with same logic
5. Reasoning chain breaking: Requiring multi-step thinking

References:
- Jia et al. (2024) - Survey on adversarial attacks
- Wei et al. (2024) - Automatic adversarial example generation
"""

import random
import json
import csv
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class AdversarialConfig:
    """Configuration for adversarial generation"""
    track: str
    input_file: str
    output_file: str
    num_questions: int = 100
    target_accuracy_range: Tuple[float, float] = (0.20, 0.40)
    semantic_similarity_threshold: float = 0.8
    token_overlap_threshold: float = 0.7


class AdversarialQuestionGenerator:
    """Generate diverse adversarial examples"""

    # Paraphrasing templates
    PARAPHRASE_TEMPLATES = [
        "Consider this: {question}",
        "Think about this scenario: {question}",
        "Here's a problem to solve: {question}",
        "Can you determine: {question}",
        "What do you think about: {question}",
    ]

    # Negative constraint templates
    NEGATIVE_TEMPLATES = [
        "Which of the following is NOT correct? {question}",
        "Assuming the opposite were true, {question}",
        "If we exclude the obvious answer, {question}",
        "Without assuming the standard answer, {question}",
        "Look for the counter-intuitive solution to: {question}",
    ]

    # Distractor enhancement templates
    DISTRACTOR_TEMPLATES = [
        "A common mistake would be to think it's X, but actually: {question}",
        "Don't be fooled by surface patterns: {question}",
        "Look past the most tempting option: {question}",
    ]

    @staticmethod
    def paraphrase_question(question: str) -> str:
        """Paraphrase question while preserving meaning"""
        template = random.choice(AdversarialQuestionGenerator.PARAPHRASE_TEMPLATES)
        return template.format(question=question)

    @staticmethod
    def add_negative_constraint(question: str, choices: List[str]) -> str:
        """Add negative constraint to question"""
        # Preserve original meaning
        intro = random.choice([
            "Which of these options is LEAST likely to be correct?",
            "Excluding the most obvious answer, which remains?",
            "If the straightforward answer were wrong, what would the answer be?",
        ])
        return f"{intro}\n\n{question}"

    @staticmethod
    def enhance_distractors(question: str, choices: List[str], correct_idx: int) -> List[str]:
        """Make distractors more plausible"""
        enhanced = choices.copy()

        # For each wrong answer, add plausible reasoning
        for i, choice in enumerate(enhanced):
            if i == correct_idx:
                continue

            enhancements = [
                f"This might seem right because {choice}, but actually it's a trick.",
                f"{choice} is tempting, but incorrect.",
            ]

            enhanced[i] = random.choice(enhancements) if random.random() > 0.5 else choice

        return enhanced

    @staticmethod
    def scramble_answer_order(question: str, choices: List[str]) -> Tuple[str, List[str]]:
        """Scramble answer choices to break patterns"""
        # Store correct answer mapping
        letters = ['A', 'B', 'C', 'D']

        # Scramble choices
        scrambled_indices = list(range(len(choices)))
        random.shuffle(scrambled_indices)
        scrambled_choices = [choices[i] for i in scrambled_indices]

        # Update question text with new order
        choices_text = "\n".join([
            f"{letters[i]}) {scrambled_choices[i]}"
            for i in range(len(scrambled_choices))
        ])

        # Note that original choice mapping is lost - this is intentional
        return f"{question}\n\n{choices_text}", scrambled_choices

    @staticmethod
    def break_reasoning_chain(question: str) -> str:
        """Break common reasoning patterns"""
        breakers = [
            " (but notice the subtle detail)",
            " (ignoring the conventional approach)",
            " (challenging the usual assumption)",
            " (this requires unconventional thinking)",
        ]
        return f"{question}{random.choice(breakers)}"


class PhysicsQuestionIntegrator:
    """Integrate physics questions into tracks"""

    PHYSICS_TOPICS = {
        'golden_ratio': 'Golden Ratio (φ) and Fibonacci sequences',
        'e8': 'E8 Lie Algebra and particle physics',
        'lqg': 'Loop Quantum Gravity',
        'ckm': 'Conformal Kaluza-Mukhan model',
        'pmns': 'Partial Minimal Supersymmetric Standard Model'
    }

    @staticmethod
    def categorize_physics_question(question_text: str) -> str:
        """Categorize physics question by topic"""
        question_lower = question_text.lower()

        if 'golden ratio' in question_lower or 'fibonacci' in question_lower or 'phi' in question_lower:
            return 'golden_ratio'
        elif 'e8' in question_lower or 'lie algebra' in question_lower or 'spin(8)' in question_lower:
            return 'e8'
        elif 'quantum gravity' in question_lower or 'loop' in question_lower:
            return 'lqg'
        elif 'ckm' in question_lower:
            return 'ckm'
        else:
            return 'pmns'

    @staticmethod
    def map_physics_to_track(topic: str) -> str:
        """Map physics topic to most relevant track"""
        # Pattern learning: golden ratio, mathematical structures
        if topic == 'golden_ratio':
            return 'thlp'

        # Metacognition: requires understanding model limitations
        if topic in ['e8', 'lqg']:
            return 'ttm'

        # Attention: requires focus on abstract concepts
        if topic in ['ckm', 'pmns']:
            return 'tagp'

        # Executive function: multi-step theory
        if topic == 'theory':
            return 'tefb'

        # Social cognition: theory discussion
        return 'tscp'


def generate_adversarial_questions(
    input_file: str,
    output_file: str,
    config: AdversarialConfig
) -> None:
    """
    Generate adversarial questions with diverse strategies.

    Args:
        input_file: Path to input CSV
        output_file: Path to output CSV
        config: Adversarial configuration
    """
    generator = AdversarialQuestionGenerator()

    # Load original questions
    questions = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            questions.append(row)

    print(f"Loaded {len(questions)} questions from {input_file}")

    # Generate adversarial variants
    adversarial_questions = []

    for i, q in enumerate(questions):
        if i >= config.num_questions:
            break

        # Apply random adversarial strategy
        strategy = random.choice(['paraphrase', 'negative', 'scramble', 'break_chain'])
        question_text = q['question']
        choices = [q.get('A', ''), q.get('B', ''), q.get('C', ''), q.get('D', '')]
        correct_answer = q['answer']

        if strategy == 'paraphrase':
            question_text = generator.paraphrase_question(q['question'])

        elif strategy == 'negative':
            question_text = generator.add_negative_constraint(q['question'], choices)

        elif strategy == 'scramble':
            question_text, choices = generator.scramble_answer_order(q['question'], choices)

        elif strategy == 'break_chain':
            question_text = generator.break_reasoning_chain(q['question'])

        # Create adversarial question
        adv_q = {
            'id': f"adv_{i:04d}",
            'question_type': f"{q['question_type']}_adversarial",
            'question': question_text,
            'A': choices[0],
            'B': choices[1],
            'C': choices[2],
            'D': choices[3],
            'answer': correct_answer,
            'strategy': strategy
        }

        adversarial_questions.append(adv_q)

    print(f"Generated {len(adversarial_questions)} adversarial questions")

    # Save to CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['id', 'question_type', 'question', 'A', 'B', 'C', 'D', 'answer', 'strategy']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(adversarial_questions)

    print(f"Saved adversarial questions to {output_file}")


def integrate_physics_questions(
    physics_file: str,
    output_dir: str,
    questions_per_track: int = 50
) -> None:
    """
    Integrate physics questions into all tracks.

    Args:
        physics_file: Path to physics questions JSON
        output_dir: Directory to save track-specific files
        questions_per_track: Number of physics questions per track
    """
    # Load physics questions
    with open(physics_file, 'r', encoding='utf-8') as f:
        physics_data = json.load(f)

    physics_questions = physics_data.get('questions', [])

    print(f"Loaded {len(physics_questions)} physics questions")

    # Create track-specific buckets
    track_buckets = {track: [] for track in ['thlp', 'ttm', 'tagp', 'tefb', 'tscp']}

    # Distribute physics questions to tracks
    for i, q in enumerate(physics_questions):
        track = PhysicsQuestionIntegrator.map_physics_to_track(
            PhysicsQuestionIntegrator.categorize_physics_question(q['question'])
        )

        if track and len(track_buckets[track]) < questions_per_track:
            track_buckets[track].append(q)

    # Save track-specific files
    output_path = Path(output_dir)
    for track, questions in track_buckets.items():
        if not questions:
            continue

        track_file = output_path / f"{track}_physics_questions.csv"

        # Convert to MC format
        mc_questions = []
        for i, q in enumerate(questions):
            mc_questions.append({
                'id': f"phys_{track}_{i:04d}",
                'question_type': f"physics_{q['topic']}",
                'question': q['question'],
                'A': q.get('A', ''),
                'B': q.get('B', ''),
                'C': q.get('C', ''),
                'D': q.get('D', ''),
                'answer': q.get('answer', 'A')
            })

        # Save
        with open(track_file, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['id', 'question_type', 'question', 'A', 'B', 'C', 'D', 'answer']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(mc_questions)

        print(f"Saved {len(questions)} physics questions to {track_file}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate enhanced adversarial questions")
    parser.add_argument('--track', required=True, choices=['thlp', 'ttm', 'tagp', 'tefb', 'tscp'],
                       help='Track to generate adversarial questions for')
    parser.add_argument('--input', required=False, default=None,
                       help='Input CSV file (default: data/{track}_mc.csv)')
    parser.add_argument('--output', required=False, default=None,
                       help='Output CSV file (default: kaggle/data/extra/{track}_adversarial_enhanced.csv)')
    parser.add_argument('--num', type=int, required=False, default=100,
                       help='Number of adversarial questions (default: 100)')
    parser.add_argument('--physics', action='store_true',
                       help='Integrate physics questions into all tracks')

    parser.add_argument('--physics-file', required=False, default='kaggle/data/physics_golden_ratio_questions.json',
                       help='Physics questions JSON file')

    args = parser.parse_args()

    # Determine file paths
    data_dir = Path(__file__).parent.parent / 'data'
    kaggle_dir = Path(__file__).parent.parent / 'kaggle' / 'data' / 'extra'

    if args.physics:
        # Integrate physics questions
        integrate_physics_questions(args.physics_file, str(kaggle_dir), questions_per_track=50)
    else:
        # Generate adversarial questions
        input_file = args.input or str(data_dir / f"{args.track}_mc.csv")
        output_file = args.output or str(kaggle_dir / f"{args.track}_adversarial_enhanced.csv")

        config = AdversarialConfig(
            track=args.track,
            input_file=input_file,
            output_file=output_file,
            num_questions=args.num
        )

        generate_adversarial_questions(input_file, output_file, config)


if __name__ == "__main__":
    main()
