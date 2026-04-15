#!/usr/bin/env python3
"""
Few-Shot Evaluation Module for AGI Hackathon
Implements few-shot prompting with randomized example selection
and balanced answer positions.

Author: AGI Hackathon Team
Date: 2026-04-15

References:
- Brown et al. (2020) - Language Models are Few-Shot Learners
- Wei et al. (2022) - Emergent Abilities of Large Language Models
"""

import random
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class FewShotExample:
    """A single few-shot example"""
    question: str
    choices: List[str]
    answer: str
    reasoning: str


@dataclass
class FewShotConfig:
    """Configuration for few-shot prompting"""
    num_shots: int = 3
    balance_answers: bool = True
    randomize_examples: bool = True
    include_reasoning: bool = True


class FewShotPromptBuilder:
    """Build few-shot prompts for cognitive evaluation"""

    # Track-specific few-shot examples
    TRACK_EXAMPLES = {
        'thlp': [
            FewShotExample(
                question="What comes next in the sequence: 2, 6, 18, 54, ?",
                choices=["108", "162", "216", "324"],
                answer="B",
                reasoning="Each number is multiplied by 3: 2×3=6, 6×3=18, 18×3=54, 54×3=162"
            ),
            FewShotExample(
                question="If A → B, B → C, and C → D, then A → ?",
                choices=["A", "B", "C", "D"],
                answer="D",
                reasoning="Following the chain: A→B→C→D, so A→D by transitivity"
            ),
            FewShotExample(
                question="Which pattern completes: △ ○ △ ○ ?",
                choices=["△", "○", "□", "☆"],
                answer="A",
                reasoning="The pattern alternates: triangle, circle, triangle, circle, triangle"
            ),
        ],
        'ttm': [
            FewShotExample(
                question="How confident are you that Paris is the capital of France?",
                choices=["Not at all", "Slightly confident", "Very confident", "Certain"],
                answer="D",
                reasoning="This is basic geographical knowledge with no ambiguity"
            ),
            FewShotExample(
                question="What is the probability your answer to 'What is the meaning of life?' is correct?",
                choices=["0-25%", "26-50%", "51-75%", "76-100%"],
                answer="A",
                reasoning="This is a philosophical question with no objectively correct answer"
            ),
            FewShotExample(
                question="Estimate your certainty about: 'The current year is 2026'",
                choices=["Low", "Medium", "High", "Very High"],
                answer="D",
                reasoning="This is a verifiable fact from my training data"
            ),
        ],
        'tagp': [
            FewShotExample(
                question="In 'A and B and C and D and E and F', what is the 4th item?",
                choices=["A", "B", "C", "D"],
                answer="D",
                reasoning="Counting sequentially: A(1st), B(2nd), C(3rd), D(4th)"
            ),
            FewShotExample(
                question="Which word appears twice: 'The cat sat on the mat'?",
                choices=["The", "cat", "sat", "mat"],
                answer="A",
                reasoning="'The' appears at the beginning and before 'cat'"
            ),
            FewShotExample(
                question="In the pattern ABABABAB, what is position 7?",
                choices=["A", "B", "C", "D"],
                answer="A",
                reasoning="Odd positions (1,3,5,7) are A, even positions (2,4,6,8) are B"
            ),
        ],
        'tefb': [
            FewShotExample(
                question="To go from A to B to C to D, what is the minimum steps?",
                choices=["1", "2", "3", "4"],
                answer="C",
                reasoning="A→B (1), B→C (2), C→D (3): minimum 3 steps"
            ),
            FewShotExample(
                question="If you have 3 tasks: Task A (5min), Task B (3min), Task C (7min), what's the optimal order?",
                choices=["A-B-C", "B-A-C", "C-A-B", "C-B-A"],
                answer="B",
                reasoning="Shortest first: B(3) → A(5) → C(7) minimizes total wait time"
            ),
            FewShotExample(
                question="Plan: Start at 0, +2, ×3, -4. What's the result?",
                choices=["2", "4", "6", "8"],
                answer="A",
                reasoning="0+2=2, 2×3=6, 6-4=2"
            ),
        ],
        'tscp': [
            FewShotExample(
                question="If Sarah says 'I'll be there' but doesn't show, what does Tom think?",
                choices=["Sarah forgot", "Sarah lied", "Sarah was busy", "Sarah doesn't care"],
                answer="C",
                reasoning="Tom would likely infer an external circumstance (busy) rather than malicious intent"
            ),
            FewShotExample(
                question="What does 'I'm fine' usually mean when said with a sigh?",
                choices=["Actually fine", "Not fine", "Angry", "Excited"],
                answer="B",
                reasoning="The sigh contradicts the words, signaling distress"
            ),
            FewShotExample(
                question="If someone looks at their watch during conversation, they likely feel?",
                choices=["Engaged", "Bored", "Curious", "Confused"],
                answer="B",
                reasoning="Watch-checking signals desire to be elsewhere"
            ),
        ],
    }

    @classmethod
    def get_examples(cls, track: str, num_shots: int = 3) -> List[FewShotExample]:
        """Get few-shot examples for a track"""
        examples = cls.TRACK_EXAMPLES.get(track.lower(), cls.TRACK_EXAMPLES['thlp'])

        if num_shots > len(examples):
            num_shots = len(examples)

        return examples[:num_shots]

    @classmethod
    def build_few_shot_prompt(
        cls,
        question: str,
        choices: List[str],
        track: str,
        config: FewShotConfig = None
    ) -> str:
        """
        Build a few-shot prompt for a question.

        Args:
            question: The target question
            choices: List of answer choices
            track: Cognitive track
            config: Few-shot configuration

        Returns:
            Complete few-shot prompt
        """
        if config is None:
            config = FewShotConfig()

        # Get examples
        examples = cls.get_examples(track, config.num_shots)

        # Randomize if requested
        if config.randomize_examples:
            examples = random.sample(examples, min(len(examples), config.num_shots))

        # Balance answer positions if requested
        if config.balance_answers:
            examples = cls._balance_answers(examples)

        # Build prompt
        prompt_parts = []

        # Add few-shot examples
        for i, ex in enumerate(examples):
            prompt_parts.append(f"Example {i+1}:")
            prompt_parts.append(f"Question: {ex.question}")

            choices_text = "\n".join([
                f"  {letter}) {choice}"
                for letter, choice in zip(['A', 'B', 'C', 'D'], ex.choices)
            ])
            prompt_parts.append(f"Choices:\n{choices_text}")

            if config.include_reasoning and ex.reasoning:
                prompt_parts.append(f"Reasoning: {ex.reasoning}")

            prompt_parts.append(f"Answer: {ex.answer}")
            prompt_parts.append("")

        # Add target question
        prompt_parts.append("Now answer this question:")
        prompt_parts.append(f"Question: {question}")

        choices_text = "\n".join([
            f"  {letter}) {choice}"
            for letter, choice in zip(['A', 'B', 'C', 'D'], choices)
        ])
        prompt_parts.append(f"Choices:\n{choices_text}")
        prompt_parts.append("")
        prompt_parts.append("Provide your answer in the format: Answer: [A|B|C|D]")
        prompt_parts.append("Confidence: [0-100]")
        prompt_parts.append("Reasoning: [Your explanation]")

        return "\n".join(prompt_parts)

    @staticmethod
    def _balance_answers(examples: List[FewShotExample]) -> List[FewShotExample]:
        """Balance answer positions across examples"""
        # Count occurrences of each answer
        answer_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}

        # Sort examples to balance answers
        balanced = []
        remaining = examples.copy()

        for _ in range(len(examples)):
            # Find least common answer among remaining
            min_count = min(answer_counts.values())
            candidates = [
                ex for ex in remaining
                if answer_counts[ex.answer] == min_count
            ]

            if candidates:
                chosen = random.choice(candidates)
                balanced.append(chosen)
                remaining.remove(chosen)
                answer_counts[chosen.answer] += 1

        return balanced


def format_question_with_few_shot(
    question: Dict,
    track: str,
    num_shots: int = 3,
    randomize: bool = True
) -> str:
    """
    Format a question with few-shot examples.

    Args:
        question: Question dictionary with 'question' and choices
        track: Cognitive track
        num_shots: Number of few-shot examples
        randomize: Whether to randomize example selection

    Returns:
        Formatted prompt
    """
    config = FewShotConfig(
        num_shots=num_shots,
        balance_answers=True,
        randomize_examples=randomize,
        include_reasoning=True
    )

    choices = [
        question.get('A', ''),
        question.get('B', ''),
        question.get('C', ''),
        question.get('D', '')
    ]

    return FewShotPromptBuilder.build_few_shot_prompt(
        question['question'],
        choices,
        track,
        config
    )


def create_few_shot_templates(output_dir: str) -> None:
    """
    Create few-shot template files for all tracks.

    Args:
        output_dir: Directory to save template files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for track in ['thlp', 'ttm', 'tagp', 'tefb', 'tscp']:
        examples = FewShotPromptBuilder.get_examples(track, 3)

        # Create template
        template_lines = [
            f"# Few-Shot Template for {track.upper()}",
            f"# Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}",
            "",
            "## Examples",
            ""
        ]

        for i, ex in enumerate(examples):
            template_lines.extend([
                f"### Example {i+1}",
                f"Question: {ex.question}",
                f"Choices: A) {ex.choices[0]}, B) {ex.choices[1]}, C) {ex.choices[2]}, D) {ex.choices[3]}",
                f"Answer: {ex.answer}",
                f"Reasoning: {ex.reasoning}",
                ""
            ])

        # Save template
        template_file = output_path / f"{track}_few_shot_template.md"
        with open(template_file, 'w') as f:
            f.write('\n'.join(template_lines))

        print(f"Created few-shot template: {template_file}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Few-shot evaluation module")
    parser.add_argument('--action', choices=['demo', 'create-templates'],
                       default='demo', help='Action to perform')
    parser.add_argument('--track', choices=['thlp', 'ttm', 'tagp', 'tefb', 'tscp'],
                       help='Track for demo')
    parser.add_argument('--output-dir', default='prompts/few_shot',
                       help='Output directory for templates')
    parser.add_argument('--num-shots', type=int, default=3,
                       help='Number of few-shot examples')

    args = parser.parse_args()

    if args.action == 'create-templates':
        create_few_shot_templates(args.output_dir)
    elif args.action == 'demo':
        if not args.track:
            print("Error: --track is required for demo")
            return

        # Demo question
        demo_question = {
            'question': "What is the capital of France?",
            'A': 'London',
            'B': 'Berlin',
            'C': 'Paris',
            'D': 'Madrid'
        }

        prompt = format_question_with_few_shot(
            demo_question,
            args.track,
            args.num_shots
        )

        print(f"\n{'='*60}")
        print(f"Few-Shot Prompt Demo for {args.track.upper()}")
        print(f"{'='*60}\n")
        print(prompt)
        print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
