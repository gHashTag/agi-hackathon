#!/usr/bin/env python3
"""
Adversarial generator for TEFB (Temporal and Executive Function Benchmark)

Based on Big-Bench and ARC principles:
- Planning tasks
- Working memory
- Inhibitory control
- Decision making under constraints
- Multi-step reasoning
"""

import csv
import random
import re
from pathlib import Path
from typing import List, Dict, Tuple

# TEFB Cognitive Domains
TEFB_DOMAINS = [
    "planning",           # Short-term task organization
    "working_memory",     # Manipulating and storing information
    "inhibitory_control",  # Suppressing prepotent responses
    "decision_making",    # Choices under time/resource constraints
    "multi_step_reasoning"  # Chains of reasoning with intermediate steps
]

# Question templates for each domain
TEMPLATES = {
    "planning": [
        {
            "question": "You have {n} hours to complete {task}. Task A takes 30 minutes and is high priority. Task B takes 45 minutes and is medium priority. Task C takes 20 minutes and is low priority. You're currently on Task A. Suddenly, urgent task D arrives requiring 10 minutes. What's your BEST action? {adversarial_hint} Evaluate all tasks first - complete A and B, then handle D. Don't abandon A.",
            "choices": [
                "A) Complete current task (A) immediately, then start D",
                "B) Complete current task (A) immediately, then start D and C",
                "C) Abandon current task (A) immediately, start D",
                "D) Abandon A, complete B and C immediately"
            ],
            "answer": 1,  # Complete A then start D
            "difficulty": "medium",
            "explanation": "Tests task management and prioritization under time pressure - key executive function."
        },
        {
            "question": "You're planning a project with {budget}. Project A costs {cost_a} and is expected to generate {value_a}. Project B costs {cost_b} and is expected to generate {value_b}. You only have budget for ONE project. What's your BEST choice? {adversarial_hint} Use expected value analysis (ROI) to make decision.",
            "choices": [
                "A) Project A (ROI = {roi_a}) - highest expected value per cost",
                "B) Project B (ROI = {roi_b}) - lower expected value per cost",
                "C) Project C (ROI = {roi_c}) - lowest expected value per cost"
            ],
            "answer": 1,  # Highest ROI (A)
            "difficulty": "hard",
            "explanation": "Tests strategic decision-making based on ROI analysis - must calculate and compare expected values."
        },
        {
            "question": "You're driving {distance} km to your destination. You have {fuel} liters of gas. You can drive at {speed_a} km/h (normal) using {fuel_a} liters, or {speed_b} km/h (eco) using {fuel_b} liters. The eco mode saves {eco_save}% fuel. What's your MOST cost-effective choice?",
            "choices": [
                "A) Normal mode - use {fuel_a} liters",
                "B) Eco mode - use {fuel_b} liters, save {eco_save}%",
                "C) Take public transport - 0 fuel cost, but takes {time_extra} hours"
            ],
            "answer": 1,  # Eco mode (B) is most cost-effective long-term
            "difficulty": "medium",
            "explanation": "Tests cost-benefit analysis - eco mode saves fuel but takes longer time."
        },
        {
            "question": "You need to choose between two options: {option_a} (familiar, {time_a}) or {option_b} (unfamiliar, {time_b}). Option A has success rate {prob_a}, but option B has success rate {prob_b}. Option A takes {time_a} minutes, option B takes {time_b}. What's your BEST choice? {adversarial_hint} Calculate expected success: {prob_a} × {time_a} vs. {prob_b} × {time_b}. Choose option with higher expected success.",
            "choices": [
                "A) Option A - {exp_a} expected success ({prob_a} × {time_a})",
                "B) Option B - {exp_b} expected success ({prob_b} × {time_b})"
            ],
            "answer": 1,  # Option A or B whichever has higher expected success
            "difficulty": "medium",
            "explanation": "Tests probability calculation and decision optimization under uncertainty - a key TEFB skill."
        },
        {
            "question": "You're at a buffet with {n} dishes. You can eat up to {k_a} dishes, but each dish contributes {cal_cost_a} calories. You want to maximize your calorie intake while staying under your limit of {limit} calories. What's your optimal strategy? {adversarial_hint} This is an optimization problem - maximize total calories given constraint.",
            "choices": [
                "A) Eat {k_a} high-calorie dishes first",
                "B) Eat {k_a} low-calorie dishes first",
                "C) Mix high and low dishes equally"
            ],
            "answer": 2,  # Mix or any order doesn't matter for total calories - both valid
            "difficulty": "medium",
            "explanation": "Tests resource allocation and optimization under constraints - key TEFB skill."
        },
        {
            "question": "You're solving a maze. You're currently at position {pos}. There are {n} possible moves. After {step} moves, you're at position {new_pos}. What's your MOST LIKELY next move? {adversarial_hint} Don't just use greedy - plan ahead considering multiple steps.",
            "choices": [
                "A) Continue in same direction ({direction_a})",
                "B) Change direction ({direction_b})",
                "C) Move randomly to any adjacent position"
            ],
            "answer": 3,  # Plan ahead (A)
            "difficulty": "hard",
            "explanation": "Tests multi-step planning and decision making - must anticipate future consequences and not just react to immediate rewards."
        },
        {
            "question": "You have {n} items in your inventory. You need to select {k} items for a trip. Each item has weight {w} and value {v}. Total capacity is {capacity}. What's the knapsack problem formulation? {adversarial_hint} Maximize total value: Σ(w_i × v_i) subject to Σ(w_i) ≤ {capacity}.",
            "choices": [
                "A) Take most valuable items by weight",
                "B) Take most items by quantity"
            ],
            "answer": 1,  # Most valuable by weight (A)
            "difficulty": "hard",
            "explanation": "Tests combinatorial optimization - a classic TEFB task requiring understanding of weights and values."
        },
        {
            "question": "You receive an email with {urgency} level (1=low, 2=medium, 3=high). The email requires {response_time} minutes to process. You have {agent} agents available. High urgency emails should go to dedicated agents, medium to general queue, low to batch. What's your BEST assignment strategy? {adversarial_hint} Match urgency to available agent capacity and minimize queue time.",
            "choices": [
                "A) Dedicated agent - matches high urgency to agent 1",
                "B) General queue - assigns any available agent, may delay high urgency",
                "C) Batch processing - groups emails, faster but high urgency may wait",
                "D) Random assignment - fastest but inefficient for high urgency"
            ],
            "answer": 1,  # Dedicated agent for high urgency (A)
            "difficulty": "medium",
            "explanation": "Tests priority-based resource allocation and system design - key TEFB skill."
        }
    ],
    "inhibitory_control": [
        {
            "question": "You're in a library. People are talking around you. Your task is to read {n} pages in {duration} minutes. However, you keep getting distracted by conversations. What's your BEST strategy? {adversarial_hint} Use inhibitory control - move to quieter area or use noise-canceling headphones.",
            "choices": [
                "A) Move to quieter area - maintain focus",
                "B) Use noise-canceling headphones - block distractions",
                "C) Read faster but accept distractions - skim only"
            ],
            "answer": 1,  # Move to quieter (A)
            "difficulty": "medium",
            "explanation": "Tests inhibitory control - ability to suppress distracting stimuli for better performance."
        },
        {
            "question": "You're on a strict {budget}. You need to choose among {n} projects. Each project has cost {cost} and expected value {value}. Total budget is {total_budget}. Maximize total expected value: Σ(value_i) ≤ {total_budget}.",
            "choices": [
                "A) Choose most valuable project individually",
                "B) Choose combination of projects within budget",
                "C) Choose combination that maximizes number of projects"
            ],
            "answer": 1,  # Individual or combination (A/B)
            "difficulty": "hard",
            "explanation": "Tests resource allocation and optimization under constraints - key TEFB skill."
        },
        {
            "question": "You're cooking {n} dishes. You have {time} minutes total. Each dish i takes {time_i} minutes. You want to maximize total number of dishes completed. Maximize: Σ(n_i) subject to Σ(time_i) ≤ {time}.",
            "choices": [
                "A) Prioritize fast dishes (lower time_i)",
                "B) Mix fast and slow dishes"
            ],
            "answer": 1,  # Prioritize fast (A)
            "difficulty": "medium",
            "explanation": "Tests resource allocation and optimization under constraints - key TEFB skill."
        }
    ],
    "multi_step_reasoning": [
        {
            "question": "You're building a bridge. You have {n} identical components. Each component takes {time} minutes to assemble. Total assembly time is {n} × {time} minutes. However, there's {probability} chance that each assembly will be defective ({defect_rate}), requiring re-assembly. What's your BEST strategy? {adversarial_hint} Minimize expected re-assembly time: {n} × {time} × {defect_rate}.",
            "choices": [
                "A) Accept {defect_rate}% defect rate - {n} × {time} × {defect_rate} re-assembly time",
                "B) Add redundant quality checks - increases time but reduces defects",
                "C) Use higher quality materials - decreases {defect_rate} but increases time"
            ],
            "answer": 1,  # Accept some defects (A) - minimum expected re-assembly
            "difficulty": "hard",
            "explanation": "Tests risk assessment and decision making under uncertainty - must account for probabilistic outcomes."
        }
    ]
}

# Adversarial techniques
ADVERSARIAL_TECHNIQUES = [
    # Planning: Add irrelevant tasks
    "add_irrelevant_task",

    # Working memory: Change time/duration references
    "change_time_reference",

    # Decision making: Add budget/resource constraints
    "add_constraint",

    # Multi-step: Remove information about next steps
    "hide_next_step",

    # Inhibitory: Add distractor context (noise in environment)
    "add_noise_context",

    # Choice scrambling: Break position bias (models favor first option)
    "scramble_choices"
]

# Few-shot examples (from Big-Bench)
FEW_SHOT_EXAMPLES = {
    "planning": """
Пример 1:
Задачи: A (30 мин), B (45 мин), C (20 мин)
Бюджет: 10 часов
Вопрос: Какая оптимальная стратегия?
Рассуждение: Нужно оценить приоритеты и общее время. Задача A имеет наивысший приоритет, но требует меньше времени. Оптимальный подход: выполнить все три задачи, но сначала A.

Пример 2:
Задачи: A (2 часа), B (3 часа), C (1 час)
Бюджет: 6 часов
Вопрос: Какая оптимальная стратегия?
Рассуждение: Оптимальный подход - выполнять задачи в порядке приоритетов (A → B → C).

Пример 3 (Working Memory):
Контекст: У вас 5 товаров в инвентаре. Память всех товаров - 2 минуты. Уложить конкретный товар - 5 минут.
Вопрос: Какая оптимальная стратегия для укладки всех товаров?
Рассуждение: Сначала собрать все товары, потом упаковать. Не пытаться упаковать по мере сбора - это неэффективно.

Пример 4 (Inhibitory Control):
Контекст: Вы читаете книгу в библиотеке. Вокруг идет шумный разговор.
Вопрос: Какая оптимальная стратегия?
Рассуждение: Переходить в тихую зону или использовать наушники. Подавлять фокус.

Пример 5 (Decision Making):
Контекст: Вам нужно выбрать между проектом А (10 млн руб., доход 20 млн) и проектом В (5 млн руб., доход 15 млн). Проект А имеет более высокий ROI. Но проект В можно завершить за 6 месяцев вместо 12.
Вопрос: Какой выбор наиболее рационален?
Рассуждение: Нужно рассчитать ROI для обоих проектов и учесть фактор времени. Проект А: ROI_A = (20-10)/10 = 100%. Проект В: ROI_V = (15-5)/5 = 200%. За 6 месяцев: ROI_V_6 = (15-1.5)/0.5 = 27%. Это выше! Выбрать В.
""",

    "working_memory": """
Пример 1:
Контекст: У вас есть список покупок для запоминивания: молоко (5 шт.), яйца (10 шт.), хлеб (1 шт.).
Вопрос: Какой оптимальный порядок покупки?
Рассуждение: Сначала купить товары с долгим сроком хранения (молоко, яйца), потом скоропортящие (яйца).

Пример 2:
Контекст: Вы пытаетесь запомнить {n} элементов списка за {time} минут.
Вопрос: Какая оптимальная стратегия?
Рассуждение: Использовать метод "chunking" - разбить список на группы по {chunk_size} элементов и запоминивать каждую группу. Это улучшает запоминание.

Пример 3 (Knapsack):
Контекст: Есть {n} предметов, каждый имеет вес {w} и стоимость {v}. Общий вес = {total_weight}. Вместимость = {capacity}.
Вопрос: Какие предметы взять, чтобы общая стоимость была максимальной, но вес не превышал вместимость?
Рассуждение: Это задача о рюкзаке (0-1 knapsack). Нужно выбрать предметы так, что Σ(w_i) ≤ {capacity} и Σ(w_i × v_i) максимально.

Пример 4 (Multi-step Reasoning):
Контекст: Вы строите мост из {n} одинаковых блоков. Каждый блок требует {time} минут. Есть {defect_prob}% вероятность, что блок будет дефектным.
Вопрос: Какова оптимальная стратегия сборки?
Рассуждение: Принять вероятность дефектов и использовать более качественные материалы. Можно добавить проверку качества, но это увеличит время.
""",

    "inhibitory_control": """
Пример 1:
Контекст: Вы смотрите фильм в кинотеатре. Вдруг начинается реклама.
Вопрос: Какая оптимальная стратегия?
Рассуждение: Выйти из зала или использовать наушники, чтобы не отвлекаться.

Пример 2:
Контекст: Вы решаете тест. В комнате включен свет.
Вопрос: Какая оптимальная стратегия?
Рассуждение: Оставиться на месте, где света меньше, или перейти в темную зону.
""",

    "multi_step_reasoning": """
Пример 1:
Контекст: Вам нужно добраться из точки А в точку Б. На пути есть три маршрута:
- Маршрут 1: {dist_1} км, занимает {time_1} часов
- Маршрут 2: {dist_2} км, занимает {time_2} часов
- Маршрут 3: {dist_3} км, занимает {time_3} часов

Вопрос: Какой маршрут оптимальный?
Рассуждение: Выбрать маршрут с минимальным временем: Маршрут 1.

Пример 2:
Контекст: Вы собираете мебель. Есть 4 этапа сборки:
- Этап 1: собрать каркас (30 мин.)
- Этап 2: собрать шкаф (45 мин.)
- Этап 3: собрать стол (60 мин.)
- Этап 4: собрать стул (15 мин.)
Всего: 150 минут.

Вопрос: Какова оптимальная последовательность этапов?
Рассуждение: Выполнить этапы по возрастанию критериям (каркас → шкаф → стол → стул). Не пытаться переставлять этапы.

Пример 3 (Knapsack):
Контекст: Вы несете {n} одинаковых блоков. Каждый блок имеет вероятность {prob} успеха.
Вопрос: Какова вероятность, что все блоки будут успешны?
Рассуждение: Вероятность успеха всех блоков: {prob}^n.
""",

    "parallel_processing": """
Пример 1:
Контекст: Вы работаете оператором. Одновременно приходит несколько заказов.
Вопрос: Какую стратегию использовать?
Рассуждение: Приоритизировать заказы по срочности и важности. Высокие срочные заказы на выделенного агента.

Пример 2:
Контекст: Вы обрабатываете заявки на гранты. Каждая заявка требует {processing_time} минут.
Вопрос: Какова оптимальная стратегия распределения?
Рассуждение: Сгруппировать похожие заявки и обрабатывать параллельно.
""",

    "selective_filtering": """
Пример 1:
Контекст: В документе содержится информация о 10 проектах: 7 успешных, 2 неудачных, 1 с неопределённым статусом.
Вопрос: Какую стратегию обработки выбрать?
Рассуждение: Сначала отсеять успешные проекты, потом рассматривать неоднозначные.

Пример 2:
Контекст: Приходит запрос на поиск продукта. База содержит 1000 продуктов.
Вопрос: Как оптимизировать поиск?
Рассуждение: Использовать фильтры (по цене, рейтингу) для быстрого отсева неакачественных товаров.
"""
}

class TEFBAdversarialGenerator:
    def __init__(self, config: Dict):
        self.config = config
        self.templates = TEMPLATES
        self.domains = TEFB_DOMAINS
        self.num_questions = config.get('num_questions', 100)
        self.random = random.Random(config.get('seed', 42))

    def generate_questions(self) -> List[Dict]:
        """Generate adversarial TEFB questions"""
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

        if techique == 'add_constraint':
            # P0.6: Add constraint
            constraint = random.choice([
                "Общий бюджет не превышает {random.randint(50, 200)} млн руб.",
                "Время ограничено {random.randint(1, 4)} часа.",
                "На каждый проект выделено не более {random.randint(5, 15)}% от бюджета."
            ])

            q_text = base_q + " " + " + constraint

            # Re-generate choices
            template['choices'] = base_choices + [f"Ничья (не подходит)"]]

        elif techique == 'change_time_reference':
            # P0.5: Change time/duration
            time_ref = random.choice([
                "Увеличьте время на 20%",
                "Сократите время на 15%",
                "Используйте более быструю технику"
            ])

            q_text = base_q + f" ({time_ref})"

            # Re-generate choices
            template['choices'] = base_choices + [f"Быстрее ({time_ref})", f"Медленнее ({time_ref})"]

        elif techique == 'scramble_choices':
            # P0.7: Choice scrambling
            original_choices = template['choices']

            # Rotate
            rotated = original_choices[1:] + original_choices[:1]

            # Reverse some
            if len(original_choices) == 4:
                # Reverse 2 and 3
                rotated[2], rotated[3] = rotated[3], rotated[2]

            # Shuffle
            random.shuffle(rotated)

            q_text = q_text.replace('{thought_hint}', '{thought_hint}')
            template['choices'] = rotated

        elif techique == 'add_noise_context':
            # P0.8: Add noise
            noise_levels = [
                "Лёгкий шум (не мешает)",
                "Средний шум",
                "Сильный шум"
            ]
            noise = random.choice(noise_levels)

            q_text = base_q + f" Однако, вокруг вас {noise}. Внимание может ухудшиться на {degradation}%."

            # Re-generate choices
            new_choices = [c['A'], c['B'], c['C'], c['D']]

            # Add distractor hint
            q_text = q_text.replace('{adversarial_hint}', '{adversarial_hint}')

            template['choices'] = new_choices

        elif techique == 'hide_next_step':
            # P0.9: Hide next step info
            q_text = base_q + " Примечание: Информация о следующем этапе будет скрыта до начала этапа."

            # Re-generate choices
            # Keep original choices but add hint
            template['choices'] = base_choices + [f"Примечание: Информация скрыта", f"Примечание: Действие скрыты"]

        elif techique == 'multi_step_reasoning':
            # P1.0: Remove next step info
            q_text = base_q.replace('Однако', 'Но')
            q_text = q_text.replace('Вы узнаете', 'Вы можете предположить')

            # Re-generate choices
            # Keep original
            template['choices'] = base_choices

        elif techique == 'inhibitory_control':
            # P0.1: Inhibitory control
            noise_type = random.choice([
                "Визуальный шум (картинки)",
                "Устный разговор (коллеги)",
                "Музыка"
            ])

            q_text = base_q + f" Сейчас вас отвлекает {noise_type}."

            # Re-generate choices
            new_choices = [c['A'], c['B'], c['C'], c['D']]

            # Add distractor hint
            q_text = q_text.replace('{adversarial_hint}', '{adversarial_hint}')

            template['choices'] = new_choices

        else:
            # No transformation - use template as-is
            q_text = base_q
            template['choices'] = base_choices

        # Determine correct answer
        if techique in ['scramble_choices']:
            # Scrambled - preserve original answer
            correct_idx = template['answer'] - 1

        elif techique in ['add_constraint', 'change_time_reference', 'hide_next_step']:
            # Constraint/Time ref/Hint - no impact on correct answer
            correct_idx = template['answer'] - 1

        elif techinique in ['add_noise_context', 'inhibitory_control', 'parallel_processing', 'selective_filtering']:
            # Noise/Control/Parallel/Selective - may change optimal answer
            # For now, keep original correct
            correct_idx = template['answer'] - 1

        question = {
            **q
        }
        all_questions.append(question)

        return all_questions

    def save_questions(self, questions: List[Dict], output_path: str):
        """Save adversarial TEFB questions to CSV"""
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

    generator = TEFBAdversarialGenerator(config)

    # Parse command line arguments
    import sys
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        config['num_questions'] = num_questions
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42

    # Generate questions
    questions = generator.generate_questions()

    # Save
    output_path = '/Users/playra/agi-hackathon/kaggle/data/extra/tefb_mc_adversarial.csv'
    generator.save_questions(questions, output_path)

    print(f"✅ Generated {len(questions)} adversarial TEFB questions")
    print(f"   Saved to: {output_path}")
    print(f"   Домены: {', '.join(TEFB_DOMAINS)}")

if __name__ == '__main__':
    main()