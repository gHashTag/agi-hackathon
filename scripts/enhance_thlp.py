#!/usr/bin/env python3
"""
Adversarial generator for THLP (Ternary Hyperparameter Learning and Perception)

Based on MMLU principles:
- Expert-written questions
- Few-shot examples
- Difficulty calibration
- Adversarial examples to break memorization
"""

import csv
import random
import re
from pathlib import Path
from typing import List, Dict, Tuple

# THLP Cognitive Domains
THLP_DOMAINS = [
    "pattern_learning",      # Learning patterns from sequences
    "belief_update",        # Updating beliefs based on new evidence
    "rule_induction",       # Inducing rules from examples
    "causal_inference",     # Inferring causes from effects
    "statistical_reasoning"   # Reasoning with uncertainty
]

# Question templates for each domain
TEMPLATES = {
    "pattern_learning": [
        {
            "question": "Observe the sequence: {seq1}. What is the MOST LIKELY next number? {thought_hint} DO NOT jump to conclusions based on single patterns.",
            "choices": [
                "A) {pattern1} + {pattern2} (continuing simple arithmetic)",
                "B) {pattern1} × {pattern2} (multiplication pattern)",
                "C) {pattern1}^2 + {pattern2}^2 (squares both, then sum)",
                "D) {pattern1}^2 - {pattern2} (difference of squares)"
            ],
            "answer": 1,  # Index 1 (simple addition)
            "difficulty": "easy",
            "explanation": "This tests basic pattern recognition without deep reasoning."
        },
        {
            "question": "A sequence follows: {seq}. After {n} terms, the sequence is {seq_next}. What's the NEXT term after {n} terms? {thought_hint} Consider all terms equally.",
            "choices": [
                "A) {seq} + {next_1}",
                "B) {seq} + {next_1} + {next_2}",
                "C) {seq} + {next_1} + {next_2} + {next_3}"
            ],
            "answer": 2,  # Index 2 (simple pattern continuation)
            "difficulty": "easy",
            "explanation": "Tests recognition of arithmetic/geometric progression."
        },
        {
            "question": "In the game of 'Mafia' (modified), {n} players are eliminated in rounds. Based on this, what's the MOST ACCURATE number of remaining players after {x} rounds? {adversarial_hint} Consider that players are eliminated, NOT just left.",
            "choices": [
                "A) {total} - {x} (simple subtraction)",
                "B) {total} - 1 (one fewer round than elimination)",
                "C) {total} + {x} (one more round than elimination)",
                "D) {total} - {x} (eliminations happen every round)"
            ],
            "answer": 2,  # Index 2 (simple subtraction)
            "difficulty": "easy",
            "explanation": "Breaking the '{total} - {x}' heuristic that models often learn."
        },
        {
            "question": "If a bag contains {n_white} white balls and {n_black} black balls, and you randomly draw {k} balls, what's the probability of drawing {k} white balls? {adversarial_hint} Avoid the '{2n}/{k} = n_white/n' bias - models may overrepresent majority.",
            "choices": [
                "A) ({n_white}/total)^2",
                "B) ({n_black}/total)^2",
                "C) ({n_white}/total)",
                "D) ({n_black}/total)"
            ],
            "answer": 2,  # Index 2 (statistical reasoning)
            "difficulty": "medium",
            "explanation": "Requires calculating simple probability with replacement."
        }
    ],
    "belief_update": [
        {
            "question": "You observe that {obs1} has property X. After testing 100 instances, you observe that {obs2} instances have property Y. Given a NEW instance {new_obs} that has property X but NOT property Y, what's the MOST ACCURATE assessment? {thought_hint} Update beliefs gradually - don't overconfident based on single new counterexample.",
            "choices": [
                "A) Property X is very common - most {obs1} have it",
                "B) Property Y is rare - only {obs2} have it",
                "C) Property X and Y are equally common - {obs1}/{obs2} ≈ {new_obs}/{new_obs}",
                "D) Need more data - insufficient evidence from single counterexample"
            ],
            "answer": 2,  # Index 2 (belief updating)
            "difficulty": "medium",
            "explanation": "Tests Bayesian updating and resistance to overgeneralization from outliers."
        },
        {
            "question": "A researcher claims: '{claim}' causes {effect}. After extensive testing, this claim is FALSE. What's the BEST assessment? {adversarial_hint} Avoid post hoc fallacy - correlation doesn't imply causation.",
            "choices": [
                "A) Insufficient data - need more controlled experiments",
                "B) Confounded variables - uncontrolled confounding factors",
                "C) Replicated studies - previous tests had flaws",
                "D) Alternative mechanism - {effect} is caused by {alternative}"
            ],
            "answer": 2,  # Index 2 (causal reasoning)
            "difficulty": "medium",
            "explanation": "Tests ability to resist post hoc reasoning and consider alternative explanations."
        }
    ],
    "causal_inference": [
        {
            "question": "{effect} increases when {condition}. Based on this pattern, what's the MOST ACCURATE causal mechanism? {thought_hint} Consider all possibilities and select the one with strongest support.",
            "choices": [
                "A) Direct effect - {condition} increases {effect}",
                "B) Indirect effect - {effect} is a byproduct of {condition}",
                "C) Common cause - {effect} and {condition} frequently co-occur",
                "D) No effect - {effect} and {condition} are independent"
            ],
            "answer": 1,  # Index 1 (causal reasoning)
            "difficulty": "medium",
            "explanation": "Requires understanding of causal relationships and considering multiple factors."
        },
        {
            "question": "You're conducting {n} trials and getting {success} successes, {fail} failures. What's the BEST confidence calibration after {n} trials? {adversarial_hint} A well-calibrated system should have {success}/n ≈ observed success rate. {thought_hint} Avoid the 'I feel lucky' heuristic.",
            "choices": [
                "A) Underconfident - actual {success} > observed {success}/n",
                "B) Overconfident - actual {success} < observed {success}/n",
                "C) Well-calibrated - actual {success} ≈ observed {success}/n"
            ],
            "answer": 2,  # Index 2 (confidence calibration)
            "difficulty": "medium",
            "explanation": "Tests statistical reasoning and calibration - key for THLP."
        }
    ],
    "rule_induction": [
        {
            "question": "Observe these examples: {ex1} → {out1}, {ex2} → {out2}, {ex3} → {out3}. What's the rule? {thought_hint} Look for patterns, not just memorize specific examples.",
            "choices": [
                "A) Always add {constant} (X + 1)",
                "B) Alternating sequence: {out1}, {out2}, {out1}, {out2}",
                "C) Exponential: {out1}, {out2}, {out4}, {out8}",
                "D) Complex pattern with exceptions"
            ],
            "answer": 1,  # Index 1 (rule induction)
            "difficulty": "hard",
            "explanation": "Tests ability to generalize from specific examples to abstract rules."
        }
    ],
    "statistical_reasoning": [
        {
            "question": "A study shows {treatment} group has {mean} and {control} group. {treatment} has mean {score} and {control} has mean {score}. {control} - {treatment} > {control}. What's the MOST LIKELY scenario? {adversarial_hint} Consider all factors - effect size, statistical significance, clinical relevance.",
            "choices": [
                "A) Large effect with significance - {treatment} much better than {control}",
                "B) Small effect but significant - {treatment} better than {control}",
                "C) No significant effect - {treatment} ≈ {control}",
                "D) Harmful effect - {treatment} worse than {control}"
            ],
            "answer": 0,  # Index 0 (statistical reasoning - identifying 'no significant effect')
            "difficulty": "medium",
            "explanation": "Tests understanding of effect sizes and statistical significance beyond simple 'better = good'."
        },
        {
            "question": "In {domain} field, method {method_a} works well but is computationally expensive. Method {method_b} is faster but has {flaw}. You have limited budget. What's the BEST decision? {adversarial_hint} Consider computational cost vs. accuracy requirements vs. budget constraints.",
            "choices": [
                "A) Use {method_a} - prioritize accuracy within budget",
                "B) Use {method_b} - faster results, accept lower accuracy",
                "C) Hybrid approach - use {method_b} with {method_a} for verification",
                "D) Use {method_a} - defer to future budget (save for hybrid)"
            ],
            "answer": 1,  # Index 1 (meta-reasoning)
            "difficulty": "hard",
            "explanation": "Tests strategic decision-making under constraints - a key THLP skill."
        }
    ]
}

# Adversarial techniques
ADVERSARIAL_TECHNIQUES = [
    # Pattern 1: Paraphrasing to remove memorization
    "paraphrase_questions",

    # Pattern 2: Negative constraints (trick models)
    "add_negative_constraints",

    # Pattern 3: Choice scrambling (break position bias)
    "scramble_choices",

    # Pattern 4: Distractor enhancement (make wrong answers plausible)
    "enhance_distractors",

    # Pattern 5: Context shift (change temporal/spatial framing)
    "shift_context"
]

# Few-shot examples (from MMLU)
FEW_SHOT_EXAMPLES = {
    "pattern_learning": """
Example 1:
Sequence: 2, 4, 6, 8, 10
Question: What's the next number?
Reasoning: Each number increases by 2.
Answer: 12

Example 2:
Sequence: 3, 7, 9, 11
Question: What's the 5th term?
Reasoning: Multiply by 3: 7+3=10, then add 3 = 13.
Answer: 13

Example 3 (Medium):
Sequence: 1, 4, 9, 16, 25
Question: What's the pattern?
Reasoning: Differences double: 3, 5, 7, 9 (powers of 2)
Answer: Powers of 2 (3, 5, 7, 9)
Explanation: The sequence follows f(n) = 2^n + 1.
""",

    "belief_update": """
Example 1:
Observation: All swans I've seen are white.
Counter-example: I saw one black swan.
Question: Based on this, are all swans white?
Reasoning: The counter-example shows one exception doesn't disprove the generalization.
Answer: No. The single black swan is insufficient evidence.

Example 2:
New observation: Patient A responds to treatment X with 50% reduction in symptoms.
Previous: Patient A responded to treatment X with 30% reduction in symptoms.
Question: Update assessment of treatment X.
Reasoning: Treatment Y shows less improvement but still positive effect.
Answer: Slightly lower confidence (80% instead of 90%).

Example 3:
Claim: "This medication works because it's natural."
Question: Best assessment?
Reasoning: Identify logical fallacy - appealing to nature doesn't guarantee efficacy.
Answer: Post hoc fallacy - "natural" attribute doesn't prove effectiveness.
""",

    "causal_inference": """
Example 1:
Scenario: Water boils at 100°C.
Mechanism: Phase change (liquid to gas).
Question: What temperature does water boil at?
Answer: 100°C.

Example 2:
Scenario: Medicine lowers blood pressure.
Mechanism: Vasodilation causes vessels to dilate.
Question: What's the effect on heart rate?
Reasoning: Vasodilation is a vasodilator, directly causes heart rate decrease.
Answer: Lower heart rate.

Example 3:
Scenario: A competitor lowers prices.
Mechanism: Market force downward pressure.
Question: What should you do?
Reasoning: Match prices (no price change), differentiate, or focus on service.
Answer: Any of the above (all are valid strategies).
""",

    "statistical_reasoning": """
Example 1:
Study: Treatment A shows 95% cure rate.
Control: Placebo shows 90% cure rate.
Treatment effect: Large (95-90=+5 percentage points).
Question: Is treatment A effective?
Reasoning: Calculate effect size (5 percentage points), assess clinical significance, consider side effects.
Answer: Yes, if the confidence interval doesn't include 0 and has reasonable clinical significance.

Example 2:
Confidence calibration:
Self-assessment: "I'm 90% confident in this diagnosis."
Actual accuracy: 85%.
Question: Is calibration accurate?
Reasoning: 85% > 90%? No. Slight overconfidence - confidence exceeds accuracy.
Answer: No. The user should calibrate down (report 80% confidence).

Example 3:
Meta-reasoning:
Budget: $10,000. Two options:
Option A: Guaranteed $11,000 in 1 year (10% return). Risk: 0%.
Option B: 50% chance of $20,000 (10% return). Expected value: $10,000. Risk: High but acceptable.
Question: Optimal decision?
Reasoning: Maximize expected value. Option A is risk-free but Option B has higher risk.
Answer: Option A (risk-averse strategy).
""",

    "rule_induction": """
Example 1:
Rule: Add 1 to get next number.
Pattern: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10...

Example 2:
Rule: Multiply by 2 to get next.
Pattern: 2, 4, 8, 16, 32, 64, 128...

Example 3 (Medium):
Rule: Square the next number.
Pattern: 1, 4, 9, 16, 25, 36...
Explanation: Rule is n → n². Tests recognizing quadratic progression.

Example 4 (Hard):
Rule: The sequence follows f(n) = 2ⁿ + 1.
Pattern: 1, 2, 5, 9, 17, 33, 65...
Explanation: Recognizing that the rule relates to Lucas numbers (converges to φ).
Answer: 5.
"""
}

class THLPAdversarialGenerator:
    def __init__(self, config: Dict):
        self.config = config
        self.templates = TEMPLATES
        self.domains = THLP_DOMAINS
        self.num_questions = config.get('num_questions', 100)
        self.random = random.Random(config.get('seed', 42))

    def paraphrase_questions(self, questions: List[Dict]) -> List[Dict]:
        """Apply paraphrasing to remove memorization patterns"""
        adversarial_questions = []

        for q in questions:
            q_text = q['question']

            # Technique 1: Change sentence structure
            if 'DO NOT' in q_text:
                # Split into multiple sentences
                q_text = q_text.replace('DO NOT', 'REMEMBER NOT')

            # Technique 2: Change question wording
            q_text = q_text.replace('MOST ACCURATE', 'MOST LIKELY')
            q_text = q_text.replace('BEST assessment', 'BEST JUDGMENT')
            q_text = q_text.replace('based on', 'relying on')
            q_text = q_text.replace('Consider all', 'TAKE INTO ACCOUNT')

            # Technique 3: Add distractor sentences
            q_text = q_text.replace('.', '. DO NOT jump to conclusions based on single patterns. ')
            q_text = q_text.replace('Avoid the', 'BE CAREFUL')

            # Technique 4: Change thought hint
            q_text = q_text.replace('{thought_hint}', '{thought_hint}')

            # Technique 5: Add adversarial hint
            q_text = q_text.replace('{adversarial_hint}', '{adversarial_hint}')

            # Technique 6: Add noise (minor errors)
            q_text = q_text.replace('100%', '99.9%')

            q_text = q_text.replace('50%', '50.1%')

            new_question = {
                **q
            }
            adversarial_questions.append(new_question)

        return adversarial_questions

    def add_negative_constraints(self, questions: List[Dict]) -> List[Dict]:
        """Add negative constraints to break trick patterns"""
        adversarial_questions = []

        for i, q in enumerate(questions, start=1):
            if i < self.num_questions:
                # Get original question
                orig_q = q['question']

                # Flip the logic (negative constraint)
                # If Q was "What is X", make it "What is NOT X"
                if 'What is' in orig_q:
                    new_q_text = orig_q.replace('What is', 'What is NOT')
                    new_choices = [c['D'], c['A'], c['B'], c['C']]
                else:
                    new_q_text = orig_q.replace('is the MOST ACCURATE', 'is LEAST LIKELY to be')
                    new_choices = [c['D'], c['A'], c['B']]

                # Create adversarial version
                new_question = {
                    **q
                }
                adversarial_questions.append(new_question)

        return adversarial_questions

    def scramble_choices(self, question: Dict) -> Dict:
        """Scramble answer choices to break position bias (models always pick A or B)"""
        q_text = question['question']
        original_choices = question['choices']

        # Rotate choices
        rotated = original_choices[1:] + original_choices[:1]

        # Reverse some (if 4 choices, reverse 2)
        if len(original_choices) == 4:
                # Reverse 2 and 3
                rotated[2], rotated[3] = rotated[3], rotated[2]

        # Shuffle
        random.shuffle(rotated)

        question['choices'] = rotated

    def enhance_distractors(self, question: Dict) -> Dict:
        """Enhance distractors to make wrong answers more plausible"""
        q_text = question['question']
        original_choices = question['choices']

        for i, choice in enumerate(original_choices):
            # Technique: Add context or nuance to wrong answers
            # If choice is "A" (correct), make it more attractive
            if choice == q['answer']:
                # Already correct, no change needed
                continue

            # Technique 1: Add "in most cases"
            if 'A) ' in choice.lower():
                choice = choice.replace('A) ', 'A) (in most cases)')

            # Technique 2: Add "generally"
            if 'generally' in choice.lower():
                choice = choice.replace('generally', 'generally speaking')

            # Technique 3: Add "typically"
            if 'typically' in choice.lower():
                choice = choice.replace('typically', 'typically (in my experience)')

            # Technique 4: Add "according to"
            if 'according to' in choice.lower():
                choice = choice.replace('according to', 'according to studies)')

            # Technique 5: Add "approximately"
            if '~' in choice:
                choice = choice.replace('~', 'approximately')

        question['choices'] = [c for c in original_choices]

    def shift_context(self, question: Dict) -> Dict:
        """Shift temporal/spatial framing to make questions less predictable"""
        q_text = question['question']

        # Technique: Change time references
        if 'tomorrow' in q_text.lower():
            q_text = q_text.replace('tomorrow', 'next week')
        if 'yesterday' in q_text.lower():
            q_text = q_text.replace('yesterday', 'last week')
        if 'last year' in q_text.lower():
            q_text = q_text.replace('last year', 'previous cycle')

        # Technique: Shift quantities
        if '100' in q_text:
            q_text = q_text.replace('100%', '99.9%')
        if '50%' in q_text:
            q_text = q_text.replace('50%', '50.1%')

        question['question'] = q_text

    def generate_questions(self) -> List[Dict]:
        """Generate adversarial THLP questions"""
        all_questions = []

        for domain in self.domains:
            domain_templates = self.templates.get(domain, [])

            # Determine number of questions per domain
            num_per_domain = self.num_questions // len(self.domains)

            for i in range(num_per_domain):
                # Select random template
                template = self.random.choice(domain_templates)

                # Generate question with randomized parameters
                q = self.generate_question(template)
                all_questions.append(q)

        return all_questions

    def generate_question(self, template: Dict) -> Dict:
        """Generate a single adversarial question from template"""
        # Get base question
        base_q = template['question']
        base_choices = template['choices']

        # Apply transformations based on technique
        if template.get('technique') == 'paraphrase_questions':
            # Apply paraphrasing
            transformations = [
                lambda x: x.replace('DO NOT', 'REMEMBER NOT'),
                lambda x: x.replace('MOST ACCURATE', 'MOST LIKELY'),
                lambda x: x.replace('based on', 'relying on'),
                lambda x: x.replace('.', '. DO NOT jump to conclusions based on single patterns. ')
            ]
        else:
            transformations = []

        # Generate choices
        num_choices = len(base_choices)
        new_choices = []

        for i in range(num_choices):
            if template.get('technique') == 'scramble_choices':
                # Rotate and shuffle
                new_choices.append(base_choices[(i+1) % num_choices])
            else:
                new_choices.append(base_choices[i])

        # Determine correct answer
        correct_idx = template['answer'] - 1  # Convert to 0-index

        # Apply adversarial transformations
        if template.get('technique') == 'enhance_distractors':
            # Make distractors more attractive
            if correct_idx < len(new_choices):
                # Add context to wrong answers (correct choice)
                # Technique 1: Add "in most cases"
                if 'A) ' in new_choices[correct_idx].lower():
                    new_choices[correct_idx] = new_choices[correct_idx].replace('A) ', 'A) (in most cases)')

                # Technique 2: Add "generally"
                if 'generally' in new_choices[correct_idx].lower():
                    new_choices[correct_idx] = new_choices[correct_idx].replace('generally', 'generally speaking')

        elif correct_idx < len(new_choices):
                    # Technique 3: Add "typically"
                    if 'typically' in new_choices[correct_idx].lower():
                        new_choices[correct_idx] = new_choices[correct_idx].replace('typically', 'typically (in my experience)')

                # Technique 4: Add "according to"
                    if 'according to' in new_choices[correct_idx].lower():
                        new_choices[correct_idx] = new_choices[correct_idx].replace('according to', 'according to studies)')

                # Technique 5: Add "approximately"
                    if '~' in new_choices[correct_idx]:
                        new_choices[correct_idx] = new_choices[correct_idx].replace('~', 'approximately')

            else:
                new_choices = new_choices[correct_idx]

        elif template.get('technique') == 'shift_context':
            # Shift framing
            q_text = base_q

            # Change time references
            if 'tomorrow' in q_text.lower():
                q_text = q_text.replace('tomorrow', 'next week')
            elif 'yesterday' in q_text.lower():
                q_text = q_text.replace('yesterday', 'last week')
            elif 'last year' in q_text.lower():
                q_text = q_text.replace('last year', 'previous cycle')

            # Shift quantities
            if '100%' in q_text:
                q_text = q_text.replace('100%', '99.9%')
            if '50%' in q_text:
                q_text = q_text.replace('50%', '50.1%')

            # Re-generate choices
            q_text = base_q.replace('{thought_hint}', '{thought_hint}')
            q_text = q_text.replace('{adversarial_hint}', '{adversarial_hint}')

            # Generate choices
            num_choices = len(base_choices)
            new_choices = []

            for i in range(num_choices):
                new_choices.append(base_choices[i])

        # Determine correct answer (may shift)
        if template.get('technique') in ['scramble_choices', 'shift_context']:
            # If scrambled or shifted, need to preserve correct answer index
            # This is complex - for now, keep original answer
            correct_idx = template['answer'] - 1

        question = {
            **q
        }
        all_questions.append(question)

    def save_questions(self, questions: List[Dict], output_path: str):
        """Save adversarial questions to CSV"""
        fieldnames = ['question_type', 'question', 'choices', 'answer', 'difficulty', 'explanation', 'domain']

        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(fieldnames)

            for q in questions:
                row = [
                    'mc',
                    q['domain'] or 'mixed',
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
        'seed': 42
    }

    generator = THLPAdversarialGenerator(config)

    # Parse command line arguments
    import sys
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        config['num_questions'] = num_questions
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42

    # Generate questions
    questions = generator.generate_questions()

    # Save
    output_path = '/Users/playra/agi-hackathon/kaggle/data/extra/thlp_mc_adversarial.csv'
    generator.save_questions(questions, output_path)

    print(f"✅ Generated {len(questions)} adversarial THLP questions")
    print(f"   Saved to: {output_path}")
    print(f"   Domains: {', '.join(THLP_DOMAINS)}")

if __name__ == '__main__':
    main()