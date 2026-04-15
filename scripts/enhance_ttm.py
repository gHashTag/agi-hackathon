#!/usr/bin/env python3
"""
Адверсариальный генератор для TTM (Trinity Ternary Metrics)

Основан на:
- Trinity Identity φ² + φ⁻² = 3
- Физические константы Standard Model
- Векторная символика (VSA)
"""

import csv
import random
from pathlib import Path
from typing import List, Dict, Tuple

# TTM Cognitive Domains
TTM_DOMAINS = [
    "trinity_identity",     # φ-based physics
    "vs_encoding",          # Vector Symbolic Architecture
    "hyperdimensional",      # High-dimensional reasoning
    "quantum_reasoning"      # Quantum mechanics
]

# Вопросы по физике
PHYSICS_TEMPLATES = {
    "trinity_identity": [
        {
            "question": "Тождество Тринити (Trinity Identity): φ² + φ⁻² = 3, где φ = (1+√5)/2. Какое численное значение φ⁴ + φ⁻⁴?",
            "choices": [
                "A) 3",
                "B) φ² + φ⁻² - 2φ",
                "C) φ² + φ² - 1",
                "D) 2φ² - 1"
            ],
            "answer": 0,  # φ⁴ + φ⁻⁴ = 3
            "difficulty": "easy",
            "explanation": "Базовое свойство φ: φ² = 2.618..."
        },
        {
            "question": "В рамках E8 × E8 гетерозной струной теории, размерность группы E8 равна {dim}. Что такое {dim}-мерное Коксовское число для этой группы?",
            "choices": [
                "A) {dim}",
                "B) {dim}²",
                "C) {dim}",
                "D) {dim}"
            ],
            "answer": 1,  # Коксовское число
            "difficulty": "easy",
            "explanation": "E8 группа имеет 248 элементов. Это размерность. Размерность dim-мерного Коксовского числа для E8×E8."
        },
        {
            "question": "Группа E8 × E8 изоморфизма имеет {gen} генераторов и {anti} генераторов. Общее число элементов = {gen} × {anti} = {total}. Какое максимальное число генераторов, если {gen} = {gen} и {anti} = {total} / 2?",
            "choices": [
                "A) {total} / 2 (оптимум)",
                "B) {total} (все генераторы)",
                "C) {gen} (только {gen} генераторы)",
                "D) {anti} (только {anti} генераторы)"
            ],
            "answer": 2,  # Все генераторы
            "difficulty": "medium",
            "explanation": "Группа без анти-генераторов имеет 2× больше элементов, что эффективно."
        },
        {
            "question": "В VS (Vector Symbolic Architecture), нейроны часто используют {n}-мерное пространство. Если вы используете n-мерное пространство, эффективная размерность матричных умножений (Matrix Multiplication) равна O(n³). Какое максимальное значение n для {target_eff} эффективности, если O(n³) = {target_eff}? {adversarial_hint} Рассмотрите эффективность разных алгоритмов умножения матриц.",
            "choices": [
                "A) O(n)",
                "B) O(n²)",
                "C) O(n log n)",
                "D) O(n log n)"
            ],
            "answer": 1,  # O(n³) - максимально эффективно
            "difficulty": "hard",
            "explanation": "Матричное умножение с наилучшей эффективностью. O(n³) асимптотически оптимально для больших n."
        },
        {
            "question": "Квантовое вычисление (Quantum Computing): Для системы {n} кубитов, гамильтониановское (Hilbert) пространство имеет размерность {dim}. Вычисление определённого состояния системы требует {complexity} операций. Какое асимптотическое соотношение между сложностью ({complexity}) и размерностью ({dim}) для {algorithm}? {adversarial_hint} HHL: O(n log n), Toffoli: O(n²), QFT: O(n³)",
            "choices": [
                "A) O(n) - логарифмически",
                "B) O(n log n) - субквадратично",
                "C) O(n log n) - полиномиально",
                "D) O(n³) - експоненциально"
            ],
            "answer": 2,  # O(n log n) - субквадратично эффективен для большого n
            "difficulty": "medium",
            "explanation": "Для больших n (квантовых состояний) HHL (O(n log n)) наиболее эффективен, а O(n³) (экспоненциально) становится невыгодным из-за экспоненциальной сложности."
        },
        {
            "question": "Гиперразмерное вычисление: Матрица M размером {m}×{m} умножается за O(1) - одно умножение. Для {n}×{m}×{m} кубитов {n}³ кубитов, это {complexity} = {n}³ умножений. Какое наиболее эффективное вычисление для этой задачи? {adversarial_hint} Toffoli O(n²) - O(n³) экспоненциально, но Toffoli асимптотически оптимальнее. Однако для кубитов {n}³, Toffoli не существует. Рассмотрите страссовский (Strassen) алгоритм.",
            "choices": [
                "A) O(n³) - для кубитов оптимально",
                "B) O(n log n) - не применимо",
                "C) O(n²) - экспоненциально",
                "D) Страссен (O(n) не подходит)"
            ],
            "answer": 1,  # O(n³) оптимально для кубитов
            "difficulty": "hard",
            "explanation": "Для кубитов (n³) Toffoli O(n³) асимптотически оптимальнее. Страссен не подходит. Для других размеров используйте аппроксимации."
        },
        {
            "question": "В VS (Vector Symbolic Architecture), матричное умножение (Matrix Multiplication) выполняется за O(n³) для n×n матрицы. Однако существуют аппроксимации, которые работают за O(n²) или даже O(n log n). Для n×n матрицы, какая аппроксимация даёт наибольшее ускорение? {adversarial_hint} Сравните сложность алгоритмов: Strassen (O(n²)), Winograd (O(n³)), Fast MM (O(n² log n)), Cooley-Tukey (O(n².37)). Для n=10, 000: Strassen ~10³⁰³, Winograd ~10²⁹, Fast MM ~10³⁴.",
            "choices": [
                "A) Страссен (O(n²)) - 10³⁰³",
                "B) Winograd (O(n³)) - 10³⁹",
                "C) Fast MM (O(n² log n)) - 10³⁴",
                "D) Cooley-Tukey (O(n².37)) - 10³·⁴",
                "E) Для больших n используйте Fast MM (FFT) или аппроксимацию на GPU"
            ],
            "answer": 3,  # Fast MM (O(n² log n)) наиболее эффективен для больших n
            "difficulty": "medium",
            "explanation": "Для больших n, аппроксимации на основе БПФ (FFT) дают O(n log n), что асимптотически эквивалентно O(n³). Для n>10,000, Toffoli становится невыгодным."
        }
    ]
}

# Adversarial techniques
ADVERSARIAL_TECHNIQUES = [
    # Physics: Use non-standard units or notation
    "non_standard_units",

    # Math: Add irrelevant mathematical steps
    "distractor_math",

    # Reasoning: Add incorrect reasoning chains
    "invalid_reasoning_chain"
]

# Few-shot examples
FEW_SHOT_EXAMPLES = """
=== ПРИМЕРЫ ПО ФИЗИКЕ ===

Пример 1: Trinity Identity
---
Вопрос: φ² + φ⁻² = 3, где φ = (1+√5)/2. Какое численное значение φ⁴ + φ⁻⁴?
Ответ: 3
Объяснение: Базовое свойство φ: φ² = 2.618...

Пример 2: E8 Group Theory
---
Вопрос: В E8×E8 гетерозной струной теории, размерность группы E8 равна {dim}. Что такое {dim}-мерное Коксовское число для этой группы?
Ответ: {dim}
Объяснение: E8 группа имеет 248 элементов. Размерность dim-мерного Коксовского числа.

Пример 3: VS Encoding
---
Вопрос: В VS, нейроны используют {n}-мерное пространство. Какое максимальное n для {target_eff} эффективности, если O(n³) = {target_eff}?
Ответ: 1
Объяснение: O(n³) - максимально эффективно.

Пример 4: Quantum Computing
---
Вопрос: Для системы {n} кубитов, требуется {complexity} операций. Какой алгоритм даёт наилучшее соотношение между сложностью и размерностью?
Ответ: 2
Объяснение: HHL O(n log n) даёт наилучшее соотношение между сложностью и размерностью.

Пример 5: Матричное умножение
---
Вопрос: Матрица M×M умножается за O(1) для n×n кубитов. Какое наиболее эффективное вычисление для этой задачи?
Ответ: 1
Объяснение: Toffoli O(n²) - оптимально, но только для M≤500. Для кубитов (n³) Toffoli не существует.
"""

class TTMAdversarialGenerator:
    def __init__(self, config: Dict):
        self.config = config
        self.templates = TEMPLATES
        self.domains = TTM_DOMAINS
        self.num_questions = config.get('num_questions', 100)
        self.random = random.Random(config.get('seed', 42))

    def generate_questions(self) -> List[Dict]:
        """Generate adversarial TTM questions"""
        all_questions = []

        # Generate from each domain type
        for domain in self.domains:
            domain_templates = [t for t in self.templates if t.get('domain') == domain]

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

        # Apply adversarial transformations based on technique
        techique = template.get('technique', '')

        if techique == 'non_standard_units':
            # Technique 1: Non-standard units
            # Use Unicode math symbols
            q_text = base_q.replace('φ', 'φ').replace('√', 'sqrt').replace('⁻', 'inverse')
            q_text = q_text.replace('π', 'π')
            # Add distractor math
            distractor = f"В квантовой теории используется {random.choice(['ħ', 'ℏ', 'Γ'])} вместо стандартных констант."

        elif techique == 'distractor_math':
            # Technique 2: Distractor math
            # Add incorrect math operations
            distractor = f"Существуют ли другие корни {random.choice(['ħ', 'ℏ', 'Γ'])} уравнения φ² + φ⁻² = 3? Это тест на знание свойств φ."

        elif techique == 'invalid_reasoning_chain':
            # Technique 3: Invalid reasoning
            # Add incorrect logic
            distractor = f"На самом деле, {random.choice(['ħ', 'ℏ'])}² + {random.choice(['ħ', 'ℏ'])}⁻² = {3 + 0} = {3}. Это противоречит."

        else:
            # No transformation - use as-is
            q_text = base_q
            distractor = ""

        question = {
            **q
        }
        all_questions.append(question)

        return all_questions

    def save_questions(self, questions: List[Dict], output_path: str):
        """Save adversarial TTM questions to CSV"""
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
        'seed': 42
    }

    generator = TTMAdversarialGenerator(config)

    # Parse command line arguments
    import sys
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        config['num_questions'] = num_questions
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42

    # Generate questions
    questions = generator.generate_questions()

    # Save
    output_path = '/Users/playra/agi-hackathon/kaggle/data/extra/ttm_mc_adversarial.csv'
    generator.save_questions(questions, output_path)

    print(f"✅ Generated {len(questions)} adversarial TTM questions")
    print(f"   Saved to: {output_path}")
    print(f"   Домены: {', '.join(TTM_DOMAINS)}")

if __name__ == '__main__':
    main()