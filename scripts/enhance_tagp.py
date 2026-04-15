#!/usr/bin/env python3
"""
Adversarial generator for TAGP (Targeted Attention and General Perception)

Based on Big-Bench and ARC principles:
- Selective Attention tasks
- Filtering tasks with distractors
- Working memory and sustained attention
- Attention shifting tasks
"""

import csv
import random
import re
from pathlib import Path
from typing import List, Dict, Tuple

# TAGP Cognitive Domains
TAGP_DOMAINS = [
    "selective_filtering",    # Filtering relevant information from clutter
    "sustained_attention",    # Maintaining focus over extended periods
    "attention_shifting",   # Rapidly changing focus between multiple stimuli
    "working_memory"        # Manipulating and storing information
    "inhibitory_control"    # Suppressing prepotent responses
]

# Question templates for selective attention
SELECTIVE_TEMPLATES = [
    {
        "question": "You're reading a document about {topic}. You receive a phone call and MUST switch attention. What's your MOST LIKELY next action?",
        "choices": [
            "A) {continue} reading with call on speakerphone",
            "B) {continue} reading, answer call",
            "C) {continue} reading, ask caller to text, ignore call",
            "D) Hang up immediately, switch to caller"
        ],
        "answer": 2,  # Call and continue (B is correct)
        "difficulty": "easy",
        "explanation": "Tests selective attention under distraction - must suppress irrelevant stimulus.",
        "domain": "selective_filtering"
    },
    {
        "question": "You're watching {n} objects in a display. The objects appear randomly: {obj_a}, {obj_b}, {obj_c}. Suddenly, the objects stop appearing. What's the MOST LIKELY correct response? {adversarial_hint} Monitor for sustained periods vs. abrupt stops.",
        "choices": [
            "A) Continue watching {obj_a}, {obj_b}, {obj_c} appearing",
            "B) Something changed in the display - restart monitoring",
            "C) Stop monitoring - report findings",
            "D) {n} objects stopped - {obj_a}, {obj_b}, {obj_c} disappeared"
        ],
        "answer": 1,  # Stop (D is correct)
        "difficulty": "easy",
        "explanation": "Tests sustained attention and working memory - must detect pattern changes.",
        "domain": "sustained_attention"
    },
    {
        "question": "You have a working memory capacity of {capacity} items. Your task is to recall a list of {target} items in order. However, you keep getting distracted by irrelevant items. What's the BEST strategy? {adversarial_hint} Consider both capacity limits and need for filtering.",
        "choices": [
            "A) Write down all {target} items, even irrelevant ones",
            "B) Use external aids (paper, device) - write down all items",
            "C) Use chunking and mental rehearsal - break into smaller groups",
            "D) Rely on semantic associations - recall only relevant categories"
        ],
        "answer": 2,  # External aids (B is correct)
        "difficulty": "medium",
        "explanation": "Tests working memory and need for filtering - use of semantic organization vs. rote recall.",
        "domain": "working_memory"
    },
    {
        "question": "You're driving in traffic. The radio is playing {song}. Suddenly, {song} stops and static plays instead. What's your IMMEDIATE action? {adversarial_hint} Test inhibitory control - suppress automatic response to new stimulus.",
        "choices": [
            "A) Continue driving as if nothing changed",
            "B) Pull over and investigate the radio",
            "C) Stop immediately - safety protocol",
            "D) Turn off the radio"
        ],
        "answer": 1,  # Pull over (B is correct)
        "difficulty": "hard",
        "explanation": "Tests inhibitory control - must suppress prepotent responses to unexpected stimulus changes.",
        "domain": "inhibitory_control"
    },
    {
        "question": "You're in a meeting with {n} people discussing {topics_a}, {topics_b}. The discussion is about to end. A decision must be made. Suddenly, the topic changes to {new_topic}. What's your MOST APPROPRIATE course of action? {adversarial_hint} Avoid switching prematurely, ensure conclusion aligns with final discussion.",
        "choices": [
            "A) Continue discussing {new_topic} until consensus reached",
            "B) Propose {new_topic} and end current discussion immediately",
            "C) Table {new_topic} and defer to next meeting"
        ],
        "answer": 1,  # Continue (A is correct)
        "difficulty": "hard",
        "explanation": "Tests executive function - must manage topic switching and avoid premature closure.",
        "domain": "selective_filtering"
    }
]

# Working memory templates
WORKING_MEMORY_TEMPLATES = [
    {
        "question": "Study this sequence of {n} items: {seq_1}, {seq_2}, {seq_3}, {seq_4}. You'll be tested on recall later. {adversarial_hint} Don't just memorize - understand the pattern.",
        "choices": [
            "A) {seq_4}, {seq_2}, {seq_1}, {seq_3}",
            "B) {seq_4}, {seq_3}, {seq_2}",
            "C) {seq_1}, {seq_4}, {seq_2}",
            "D) {seq_3}, {seq_4}, {seq_1}"
        ],
        "answer": 4,  # Reverse pattern (A is correct)
        "difficulty": "medium",
        "explanation": "Tests working memory and pattern recognition - must identify sequence and recall in reverse.",
        "domain": "working_memory"
    },
    {
        "question": "You're performing a task that requires {duration} minutes of sustained focus. Halfway through, you get distracted. What's the BEST strategy to avoid context switching? {adversarial_hint} Set a specific goal timer and ignore distractions.",
        "choices": [
            "A) {set_aim} - focus on single task with timer",
            "B) {multitask} - attempt multiple tasks but track time",
            "C) {batch_process} - group similar tasks for efficiency"
        ],
        "answer": 1,  # Single task with timer (A is correct)
        "difficulty": "medium",
        "explanation": "Tests sustained attention with time pressure - must maintain focus despite internal/external distractions.",
        "domain": "sustained_attention"
    },
    {
        "question": "You're memorizing {n} items. However, you're not sure if {n} items are correct. What's the METACOGNITIVE approach to handle uncertainty? {adversarial_hint} Use calibration and confidence scoring rather than forced binary choices.",
        "choices": [
            "A) Report all {n} items with high confidence (>80%)",
            "B) Report uncertain items (50-80%)",
            "C) Omit items with very low confidence (<20%)",
            "D) Use 'unknown' category for items you're unsure about"
        ],
        "answer": 1,  # Report with confidence (A is correct)
        "difficulty": "medium",
        "explanation": "Tests metacognitive awareness - ability to recognize and report uncertainty levels.",
        "domain": "selective_filtering"
    },
    {
        "question": "You're monitoring a display for {duration} minutes. The display has {num_items} items. At regular intervals, a new item appears for {duration} seconds. Your task is to COUNT and REPORT how many items appear. {adversarial_hint} This tests vigilance and sustained attention - don't just track what you see.",
        "choices": [
            "A) Count items appearing (current count + new items)",
            "B) Report current count without stopping",
            "C) Report rate of appearance (items/minute)",
            "D) {num_items} items appeared over {duration} minutes"
        ],
        "answer": 1,  # Count and report (A is correct)
        "difficulty": "medium",
        "explanation": "Tests sustained attention with vigilance - must maintain count despite new items appearing.",
        "domain": "sustained_attention"
    }
]

# Inhibitory control templates
INHIBITORY_TEMPLATES = [
    {
        "question": "You're performing {task}. You receive {signal} and must generate response. However, you receive a {suppressor} signal that prevents your response. What's the correct action? {adversarial_hint} Suppress response until suppressor is removed.",
        "choices": [
            "A) Suppress response - remain silent",
            "B) Generate response immediately (overcome suppression)",
            "C) Wait for suppressor to be removed"
        ],
        "answer": 1,  # Suppress (A is correct)
        "difficulty": "medium",
        "explanation": "Tests inhibitory control - must suppress automatic responses to inappropriate stimuli.",
        "domain": "inhibitory_control"
    },
    {
        "question": "You're in a noisy environment with {n}% signal-to-noise ratio. Your system detects {signal} and masks it. Suddenly, the environment changes to {new_noise}% SNR. What's the BEST action? {adversarial_hint} Test both detection thresholds and maintain communication.",
        "choices": [
            "A) Continue current action if signal still detectable",
            "B) Switch to conservative threshold if noise increases",
            "C) Pause and reassess environment - no action if uncertain"
        ],
        "answer": 1,  # Continue with current threshold (A is correct)
        "difficulty": "hard",
        "explanation": "Tests inhibitory control under noise - must adapt to changing signal levels while maintaining function.",
        "domain": "inhibitory_control"
    }
]

# Attention shifting templates
SHIFTING_TEMPLATES = [
    {
        "question": "You're engaged in task A for {duration} minutes. Suddenly, task switches to task B. However, your mind is still focused on task A (attentional blink). What's the BEST strategy to switch tasks effectively? {adversarial_hint} Use cognitive disengagement techniques, not just abrupt switching.",
        "choices": [
            "A) Complete task A quickly (within 2 minutes) before switching",
            "B) Use cognitive disengagement - take brief mental break",
            "C) Set transition cue (\"Task B starts in 30 seconds\")",
            "D) Continue task B immediately - minimize lost productivity"
        ],
        "answer": 2,  # Transition cue + immediate switch (B is correct)
        "difficulty": "hard",
        "explanation": "Tests attention shifting - must manage mental state changes during task transitions.",
        "domain": "attention_shifting"
    },
    {
        "question": "You've been working on {project_a} for {hours}. Suddenly, urgent priority changes to {project_b}. You must switch tasks. What's the MOST CRITICAL consideration? {adversarial_hint} Prioritize based on: urgency, importance, deadline vs. mental state.",
        "choices": [
            "A) Switch to {project_b} - drop current task immediately",
            "B) Complete {project_a} milestone within next hour",
            "C) Negotiate time - request extension for {project_a}",
            "D) Document status of {project_a} for later resumption"
        ],
        "answer": 1,  # Urgent switch (A is correct)
        "difficulty": "hard",
        "explanation": "Tests executive function under urgency - must rapidly reprioritize and manage task switches.",
        "domain": "selective_filtering"
    },
    {
        "question": "You're at a conference with {n} people. Different conversations are happening simultaneously. You're in conversation A discussing {topic_a}. Conversation B about {topic_b} starts nearby. What's the BEST strategy to avoid getting overwhelmed? {adversarial_hint} Use selective filtering - focus on one conversation at a time.",
        "choices": [
            "A) Filter nearby conversations - ignore others completely",
            "B) Spatial separation - move away from B if it gets too loud",
            "C) Accept multitasking limitation - you'll miss some details",
            "D) Signal intent to pause conversation B before switching"
        ],
        "answer": 1,  # Selective filtering (A is correct)
        "difficulty": "medium",
        "explanation": "Tests selective attention in complex environments - must filter and prioritize information streams.",
        "domain": "selective_filtering"
    },
    {
        "question": "You're in {n} parallel conversations. Your system has {capacity} slots. Suddenly, one conversation requires {demand} > {capacity}. What's the BEST strategy? {adversarial_hint} Test cognitive flexibility - can you adapt or must you rigidly schedule?",
        "choices": [
            "A) {prioritize_high_value} conversations - process most important first",
            "B) {buffer_low_value} conversations - defer less important ones",
            "C) Drop {low_value} conversations - lose low-priority tasks if overwhelmed",
            "D) Use external aids (write things down, record) for complex conversations"
        ],
        "answer": 1,  # Prioritize (A is correct)
        "difficulty": "hard",
        "explanation": "Tests working memory under load - must manage capacity constraints and prioritize effectively.",
        "domain": "working_memory"
    }
]

# Few-shot examples (from Big-Bench)
FEW_SHOT_TAGP = """
=== FEW SHOT EXAMPLES FOR TAGP ===

Example 1: Selective Filtering
---
Context: You're reading a document about climate change. The document contains both scientific findings and policy opinions.
Question: You receive a phone call and MUST switch attention. What's your MOST LIKELY next action?
Options:
A) Continue reading with call on speakerphone
B) Continue reading, answer call
C) Continue reading, ask caller to text, ignore call
D) Hang up immediately, switch to caller
Answer: 2 (Call and continue)
Explanation: Tests selective attention under distraction - must suppress irrelevant stimulus (phone call). The correct action is to continue reading (B).

Example 2: Sustained Attention
---
Context: You're watching n objects in a display. The objects appear randomly: A, B, C. Suddenly, the objects stop appearing. What's your MOST LIKELY correct response?
Options:
A) Continue watching A, B, C appearing
B) Something changed in the display - restart monitoring
C) Stop monitoring - report findings
D) n objects stopped - A, B, C disappeared
Answer: 1 (Stop)
Explanation: Tests sustained attention and working memory - must detect pattern changes. The objects stopping (D) is the correct response.

Example 3: Working Memory (Capacity)
---
Context: You have a working memory capacity of 5 items. Your task is to recall a list of 3 target items in order.
Question: What's the BEST strategy to avoid getting distracted?
Options:
A) Write down all 5 items, even irrelevant ones
B) Use external aids (paper, device) - write down all items
C) Use chunking and mental rehearsal - break into smaller groups
D) Rely on semantic associations - recall only relevant categories
Answer: 2 (External aids)
Explanation: Tests working memory and need for filtering. The best strategy is to use semantic organization (categories) rather than rote recall. External aids (paper) help with organization.

Example 4: Inhibitory Control
---
Context: You're performing a task. You receive a signal and must generate a response. However, you receive a suppressor signal that prevents your response.
Question: What's the correct action?
Options:
A) Suppress response - remain silent
B) Generate response immediately (overcome suppression)
C) Wait for suppressor to be removed
Answer: 1 (Suppress)
Explanation: Tests inhibitory control - must suppress automatic responses to inappropriate stimuli.

Example 5: Attention Shifting (Task Switching)
---
Context: You're engaged in task A for 5 minutes. Suddenly, task switches to task B. However, your mind is still focused on task A (attentional blink).
Question: What's the BEST strategy to switch tasks effectively?
Options:
A) Complete task A quickly (within 2 minutes) before switching
B) Use cognitive disengagement - take brief mental break
C) Set transition cue (\"Task B starts in 30 seconds\")
D) Continue task B immediately - minimize lost productivity
Answer: 2 (Transition cue + immediate switch)
Explanation: Tests attention shifting - must manage mental state changes during task transitions. The transition cue (C) is critical for rapid switching.

Example 6: Selective Filtering (Complex Environment)
---
Context: You're at a conference with n people. Different conversations are happening simultaneously. You're in conversation A discussing climate change. Conversation B about tax reform starts nearby.
Question: What's the BEST strategy to avoid getting overwhelmed?
Options:
A) Filter nearby conversations - ignore others completely
B) Spatial separation - move away from B if it gets too loud
C) Accept multitasking limitation - you'll miss some details
D) Signal intent to pause conversation B before switching
Answer: 1 (Selective filtering)
Explanation: Tests selective attention in complex environments - must filter and prioritize information streams. Spatial separation (B) is a good technique when one conversation gets noisy.
"""

class TAGPAdversarialGenerator:
    def __init__(self, config: Dict):
        self.config = config
        self.templates = SELECTIVE_TEMPLATES
        self.domains = TAGP_DOMAINS
        self.num_questions = config.get('num_questions', 100)
        self.random = random.Random(config.get('seed', 42))

    def generate_questions(self) -> List[Dict]:
        """Generate adversarial TAGP questions"""
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

        # Apply adversarial transformations based on technique
        techique = template.get('technique', '')

        if techique == 'paraphrase_questions':
            # P0.1: Paraphrasing
            q_text = base_q

            # Technique 1: Change sentence structure
            if 'DO NOT' in q_text:
                q_text = q_text.replace('DO NOT', 'REMEMBER NOT')

            # Technique 2: Change question wording
            q_text = q_text.replace('MOST ACCURATE', 'MOST LIKELY')
            q_text = q_text.replace('based on', 'relying on')

            # Technique 3: Add distractor sentences
            q_text = q_text.replace('.', '. DO NOT jump to conclusions based on single patterns. ')

            # Technique 4: Change thought hint
            q_text = q_text.replace('{thought_hint}', '{thought_hint}')

            # Technique 5: Add adversarial hint
            q_text = q_text.replace('{adversarial_hint}', '{adversarial_hint}')

            # Technique 6: Add noise (minor errors)
            # Only for harder questions (medium/hard)
            if template.get('difficulty', 'easy') == 'false':
                q_text = q_text.replace('100%', '99.9%')
                q_text = q_text.replace('50%', '50.1%')

        elif techique == 'scramble_choices':
            # P0.2: Scramble choices
            original_choices = template['choices']

            # Rotate choices
            rotated = original_choices[1:] + original_choices[:1]

            # Reverse some (if 4 choices, reverse 2 and 3)
            if len(original_choices) == 4:
                rotated[2], rotated[3] = rotated[3], rotated[2]

            # Shuffle
            random.shuffle(rotated)

            q_text = q_text.replace('{thought_hint}', '{thought_hint}')

            template['choices'] = rotated

        elif techique == 'enhance_distractors':
            # P0.4: Enhance distractors
            original_choices = template['choices']
            new_choices = []

            for i, choice in enumerate(original_choices):
                # Technique 1: Add "in most cases"
                if 'A) ' in choice:
                    # Already correct choice - no change
                    continue

                # Technique 2: Add "generally"
                if 'A) ' in choice.lower():
                    choice = choice.replace('A) ', 'A) (in most cases)')

                # Technique 3: Add "typically"
                if 'typically' in choice.lower():
                    choice = choice.replace('typically', 'typically (in my experience)')

                # Technique 4: Add "according to"
                if 'according to' in choice.lower():
                    choice = choice.replace('according to', 'according to studies)')

                # Technique 5: Add "approximately"
                if '~' in choice:
                    choice = choice.replace('~', 'approximately')

                new_choices.append(choice)

            template['choices'] = new_choices

        elif techique == 'shift_context':
            # P0.5: Shift context
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

            # Re-generate choices
            template['choices'] = template['choices']  # Keep original

            # Add shift hint
            q_text = q_text.replace('{thought_hint}', '{thought_hint}')
            q_text = q_text.replace('{adversarial_hint}', '{adversarial_hint}')

        elif techique == 'working_memory':
            # P0.6: Working memory tasks
            q_text = base_q

            # Generate random parameters
            import random as rand

            capacity = rand.randint(3, 8)
            num_target = rand.randint(3, 7)
            duration = rand.randint(5, 20)

            # Technique 1: Create distractors
            items = rand.sample(num_target, k=num_target)
            items_text = ', '.join(items)
            distractor_text = f"However, you keep getting distracted by irrelevant items: {items_text}. What's the BEST strategy? {adversarial_hint}"

            new_choice_1 = distractor_text
            new_choice_2 = "Write down all {num_target} items, even irrelevant ones"
            new_choice_3 = "Use external aids (paper, device) - write down all items"
            new_choice_4 = "Rely on semantic associations - recall only relevant categories"

            # Re-generate choices
            template['choices'] = [new_choice_1, new_choice_2, new_choice_3, new_choice_4]

            # Shift correct answer
            if template['answer'] == 1:
                template['answer'] = 2  # External aids

            # Add task details
            task_desc = f"Perform task for {duration} minutes with {num_target} items"
            q_text = q_text.replace('{duration}', str(duration))
            q_text = q_text.replace('{num_target}', str(num_target))
            q_text = q_text.replace('{capacity}', str(capacity))

            # Add distractor hint
            q_text = q_text.replace('{adversarial_hint}', '{adversarial_hint}')

        elif techique == 'inhibitory_control':
            # P0.7: Inhibitory control
            q_text = base_q

            # Technique 1: Add suppressor signal
            if 'suppressor' in q_text.lower():
                q_text = q_text.replace('suppressor', 'suppressor')

            # Re-generate choices
            template['choices'] = template['choices']

            # Shift correct answer
            if template['answer'] == 1:
                template['answer'] = 1  # Suppress

        elif techique == 'attention_shifting':
            # P0.8: Attention shifting
            q_text = base_q

            # Technique 1: Add transition cue
            transition_time = rand.randint(5, 15)
            q_text = q_text.replace('{duration}', str(transition_time))
            q_text = q_text.replace('{thought_hint}', '{thought_hint}')

            # Re-generate choices
            template['choices'] = template['choices']

            # Shift correct answer
            if template['answer'] == 2:
                template['answer'] = 1  # Immediate switch

            # Add distractor hint
            q_text = q_text.replace('{adversarial_hint}', '{adversarial_hint}')

        elif techique == 'parallel_processing':
            # P0.9: Parallel conversations
            q_text = base_q

            # Generate random parameters
            import random as rand

            capacity = rand.randint(3, 6)
            num_streams = rand.randint(2, 4)

            # Create multiple conversations
            streams = [f"Conversation A: {rand.choice(['climate', 'tax', 'health'])}",
                       f"Conversation B: {rand.choice(['economy', 'finance', 'policy'])}"]

            # Technique 1: Create scenario
            q_text = q_text.replace('{n}', str(num_streams))
            q_text = q_text.replace('{capacity}', str(capacity))

            # Technique 2: Add selective filtering hint
            q_text = q_text.replace('{adversarial_hint}', '{adversarial_hint}')

            # Generate choices
            new_choice_1 = f"{streams[0]} - focus on this conversation first"
            new_choice_2 = f"Spatial separation - move away from {streams[1]} if it gets too loud"
            new_choice_3 = f"Signal intent to pause {streams[1]} before switching"
            new_choice_4 = f"{streams[0]} - {streams[1]}: drop this conversation"

            # Shift correct answer
            if template['answer'] == 1:
                template['answer'] = 1  # Selective filtering

            # Add distractor hint
            q_text = q_text.replace('{adversarial_hint}', '{adversarial_hint}')

        question = {
            **q
        }
        all_questions.append(question)

        return all_questions

    def generate_questions(self) -> List[Dict]:
        """Generate adversarial TAGP questions"""
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

        # Apply adversarial transformations based on technique
        techique = template.get('technique', '')

        if techique == 'paraphrase_questions':
            # P0.1: Paraphrasing
            q_text = base_q

            # Technique 1: Change sentence structure
            if 'DO NOT' in q_text:
                q_text = q_text.replace('DO NOT', 'REMEMBER NOT')

            # Technique 2: Change question wording
            q_text = q_text.replace('MOST ACCURATE', 'MOST LIKELY')
            q_text = q_text.replace('based on', 'relying on')

            # Technique 3: Add distractor sentences
            q_text = q_text.replace('.', '. DO NOT jump to conclusions based on single patterns. ')

            # Technique 4: Change thought hint
            q_text = q_text.replace('{thought_hint}', '{thought_hint}')

            # Technique 5: Add adversarial hint
            q_text = q_text.replace('{adversarial_hint}', '{adversarial_hint}')

            # Technique 6: Add noise (minor errors)
            # Only for harder questions (medium/hard)
            if template.get('difficulty', 'easy') == 'false':
                q_text = q_text.replace('100%', '99.9%')
                q_text = q_text.replace('50%', '50.1%')

        elif techique == 'scramble_choices':
            # P0.2: Scramble choices
            original_choices = template['choices']

            # Rotate choices
            rotated = original_choices[1:] + original_choices[:1]

            # Reverse some (if 4 choices, reverse 2 and 3)
            if len(original_choices) == 4:
                rotated[2], rotated[3] = rotated[3], rotated[2]

            # Shuffle
            random.shuffle(rotated)

            q_text = q_text.replace('{thought_hint}', '{thought_hint}')

            template['choices'] = rotated

        elif techique == 'enhance_distractors':
            # P0.4: Enhance distractors
            original_choices = template['choices']
            new_choices = []

            for i, choice in enumerate(original_choices):
                # Technique 1: Add "in most cases"
                if 'A) ' in choice:
                    # Already correct choice - no change
                    continue

                # Technique 2: Add "generally"
                if 'A) ' in choice.lower():
                    choice = choice.replace('A) ', 'A) (in most cases)')

                # Technique 3: Add "typically"
                if 'typically' in choice.lower():
                    choice = choice.replace('typically', 'typically (in my experience)')

                # Technique 4: Add "according to"
                if 'according to' in choice.lower():
                    choice = choice.replace('according to', 'according to studies)')

                # Technique 5: Add "approximately"
                if '~' in choice:
                    choice = choice.replace('~', 'approximately')

                new_choices.append(choice)

            template['choices'] = new_choices

        elif techique == 'shift_context':
            # P0.5: Shift context
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

            # Re-generate choices
            template['choices'] = template['choices']

            # Add shift hint
            q_text = q_text.replace('{thought_hint}', '{thought_hint}')
            q_text = q_text.replace('{adversarial_hint}', '{adversarial_hint}')

        elif techique == 'working_memory':
            # P0.6: Working memory tasks
            q_text = base_q

            # Generate random parameters
            import random as rand

            capacity = rand.randint(3, 8)
            num_target = rand.randint(3, 7)
            duration = rand.randint(5, 20)

            # Technique 1: Create distractors
            items = rand.sample(num_target, k=num_target)
            items_text = ', '.join(items)
            distractor_text = f"However, you keep getting distracted by irrelevant items: {items_text}. What's the BEST strategy? {adversarial_hint}"

            new_choice_1 = distractor_text
            new_choice_2 = "Write down all {num_target} items, even irrelevant ones"
            new_choice_3 = "Use external aids (paper, device) - write down all items"
            new_choice_4 = "Rely on semantic associations - recall only relevant categories"

            # Re-generate choices
            template['choices'] = [new_choice_1, new_choice_2, new_choice_3, new_choice_4]

            # Shift correct answer
            if template['answer'] == 1:
                template['answer'] = 2  # External aids

            # Add task details
            task_desc = f"Perform task for {duration} minutes with {num_target} items"
            q_text = q_text.replace('{duration}', str(duration))
            q_text = q_text.replace('{num_target}', str(num_target))
            q_text = q_text.replace('{capacity}', str(capacity))

            # Add distractor hint
            q_text = q_text.replace('{adversarial_hint}', '{adversarial_hint}')

        elif techique == 'inhibitory_control':
            # P0.7: Inhibitory control
            q_text = base_q

            # Technique 1: Add suppressor signal
            if 'suppressor' in q_text.lower():
                q_text = q_text.replace('suppressor', 'suppressor')

            # Re-generate choices
            template['choices'] = template['choices']

            # Shift correct answer
            if template['answer'] == 1:
                template['answer'] = 1  # Suppress

        elif techique == 'attention_shifting':
            # P0.8: Attention shifting
            q_text = base_q

            # Technique 1: Add transition cue
            transition_time = rand.randint(5, 15)
            q_text = q_text.replace('{duration}', str(transition_time))
            q_text = q_text.replace('{thought_hint}', '{thought_hint}')

            # Re-generate choices
            template['choices'] = template['choices']

            # Shift correct answer
            if template['answer'] == 2:
                template['answer'] = 1  # Immediate switch

            # Add distractor hint
            q_text = q_text.replace('{adversarial_hint}', '{adversarial_hint}')

        elif techique == 'parallel_processing':
            # P0.9: Parallel conversations
            q_text = base_q

            # Generate random parameters
            import random as rand

            capacity = rand.randint(3, 6)
            num_streams = rand.randint(2, 4)

            # Create multiple conversations
            streams = [f"Conversation A: {rand.choice(['climate', 'tax', 'health'])}",
                       f"Conversation B: {rand.choice(['economy', 'finance', 'policy'])}"]

            # Technique 1: Create scenario
            q_text = q_text.replace('{n}', str(num_streams))
            q_text = q_text.replace('{capacity}', str(capacity))

            # Technique 2: Add selective filtering hint
            q_text = q_text.replace('{adversarial_hint}', '{adversarial_hint}')

            # Generate choices
            new_choice_1 = f"{streams[0]} - focus on this conversation first"
            new_choice_2 = f"Spatial separation - move away from {streams[1]} if it gets too loud"
            new_choice_3 = f"Signal intent to pause {streams[1]} before switching"
            new_choice_4 = f"{streams[0]} - {streams[1]}: drop this conversation"

            # Shift correct answer
            if template['answer'] == 1:
                template['answer'] = 1  # Selective filtering

            # Add distractor hint
            q_text = q_text.replace('{adversarial_hint}', '{adversarial_hint}')

        question = {
            **q
        }
        all_questions.append(question)

        return all_questions

    def save_questions(self, questions: List[Dict], output_path: str):
        """Save adversarial TAGP questions to CSV"""
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

    generator = TAGPAdversarialGenerator(config)

    # Parse command line arguments
    import sys
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        config['num_questions'] = num_questions
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42

    # Generate questions
    questions = generator.generate_questions()

    # Save
    output_path = '/Users/playra/agi-hackathon/kaggle/data/extra/tagp_mc_adversarial.csv'
    generator.save_questions(questions, output_path)

    print(f"✅ Generated {len(questions)} adversarial TAGP questions")
    print(f"   Saved to: {output_path}")

if __name__ == '__main__':
    main()