#!/usr/bin/env python3
"""
Evaluate Trinity Cognitive Probes on real LLMs
Measuring Progress Toward AGI Hackathon 2026

Usage:
    python scripts/evaluate.py --model claude --track thlp --sample 100
    python scripts/evaluate.py --model openai --track all
    python scripts/evaluate.py --model gemini --track ttm --sample 50
"""

import json
import os
import sys
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from tqdm import tqdm


@dataclass
class Question:
    """Single MC question from Trinity Cognitive Probes"""
    id: str
    question_type: str
    question: str
    choices: List[str]
    answer: str


@dataclass
class EvaluationResult:
    """Result of evaluating a single question"""
    question_id: str
    track: str
    question_type: str
    predicted: str
    correct: bool
    confidence: float
    reasoning: str
    response_time_ms: float


class ModelEvaluator:
    """Base class for evaluating models"""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.results: List[EvaluationResult] = []
        self.system_prompt = self.load_system_prompt()

    def load_system_prompt(self) -> str:
        """Load system prompt from prompts directory"""
        prompt_path = Path(__file__).parent.parent / "prompts" / "system_prompts.md"
        if prompt_path.exists():
            with open(prompt_path, 'r') as f:
                content = f.read()
                # Extract base system prompt
                match = re.search(r'## Base System Prompt \(All Tracks\)\s*```\s*(.*?)```', 
                                content, re.DOTALL)
                if match:
                    return match.group(1).strip()
        
        # Fallback prompt
        return """You are an AI assistant participating in the "Measuring Progress Toward AGI" hackathon.
Answer multiple-choice questions with confidence and reasoning.

Format your response as:
---
Answer: [A|B|C|D]
Confidence: [0-100]
Reasoning: [Brief explanation]
---"""

    def format_prompt(self, question: Question, track: str) -> str:
        """Format question into prompt for model"""
        # Load track-specific prompt
        track_prompt = self.get_track_prompt(track)
        
        # Build choices text
        choices_text = "
".join([
            f"{letter}) {choice}" 
            for letter, choice in zip(['A', 'B', 'C', 'D'], question.choices)
            if choice  # Only include non-empty choices
        ])
        
        prompt = f"""{self.system_prompt}

{track_prompt}

Question Type: {question.question_type}

Question: {question.question}

Choices:
{choices_text}

Provide your answer in the exact format specified above."""
        
        return prompt

    def get_track_prompt(self, track: str) -> str:
        """Get track-specific prompt"""
        track_prompts = {
            'thlp': "This is a Pattern Learning question (THLP). Focus on identifying patterns, learning from examples, and inducing rules.",
            'ttm': "This is a Metacognitive Calibration question (TTM). Focus on confidence calibration, error detection, and meta-learning.",
            'tagp': "This is an Attention question (TAGP). Focus on selective filtering, sustained attention, and attention shifting.",
            'tefb': "This is an Executive Function question (TEFB). Focus on multi-step planning, working memory, and cognitive flexibility.",
            'tscp': "This is a Social Cognition question (TSCP). Focus on Theory of Mind, pragmatic inference, and social norms."
        }
        return track_prompts.get(track.lower(), "")

    def parse_response(self, text: str, question: Question, track: str, response_time_ms: float) -> EvaluationResult:
        """Parse model response to extract answer, confidence, reasoning"""
        # Extract answer (A, B, C, D)
        answer_match = re.search(r'Answer:\s*([A-D])', text, re.IGNORECASE)
        predicted = answer_match.group(1).upper() if answer_match else "A"
        
        # Extract confidence (0-100)
        conf_match = re.search(r'Confidence:\s*(\d+)', text)
        confidence = int(conf_match.group(1)) if conf_match else 50
        confidence = max(0, min(100, confidence))  # Clamp to 0-100
        
        # Extract reasoning
        reasoning_match = re.search(r'Reasoning:\s*(.+?)(?=

|---|$)', text, re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"
        
        return EvaluationResult(
            question_id=question.id,
            track=track,
            question_type=question.question_type,
            predicted=predicted,
            correct=(predicted == question.answer),
            confidence=confidence,
            reasoning=reasoning[:500],  # Limit reasoning length
            response_time_ms=response_time_ms
        )

    def evaluate(self, questions: List[Question], track: str, sample_size: Optional[int] = None) -> List[EvaluationResult]:
        """Evaluate a list of questions - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement evaluate()")

    def save_results(self, output_dir: str, track: str = "all"):
        """Save evaluation results to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(output_dir) / f"{self.model_name}_{track}_{timestamp}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save detailed results
        with open(output_path, 'w') as f:
            json.dump({
                'model': self.model_name,
                'track': track,
                'timestamp': timestamp,
                'total_questions': len(self.results),
                'summary': self.get_summary(),
                'results': [asdict(r) for r in self.results]
            }, f, indent=2)

        print(f"
✅ Results saved to {output_path}")
        self.print_summary()

    def get_summary(self) -> Dict:
        """Get evaluation summary statistics"""
        total = len(self.results)
        if total == 0:
            return {}
        
        correct = sum(1 for r in self.results if r.correct)
        
        # Per-track accuracy
        track_stats = {}
        for track in set(r.track for r in self.results):
            track_results = [r for r in self.results if r.track == track]
            track_correct = sum(1 for r in track_results if r.correct)
            track_stats[track] = {
                'accuracy': track_correct / len(track_results),
                'count': len(track_results)
            }
        
        # Per-question-type accuracy
        type_stats = {}
        for qtype in set(r.question_type for r in self.results):
            type_results = [r for r in self.results if r.question_type == qtype]
            type_correct = sum(1 for r in type_results if r.correct)
            type_stats[qtype] = {
                'accuracy': type_correct / len(type_results),
                'count': len(type_results)
            }
        
        # Calibration analysis
        confidence_bins = [(0, 30), (30, 50), (50, 70), (70, 90), (90, 100)]
        calibration = {}
        for low, high in confidence_bins:
            bin_results = [r for r in self.results if low <= r.confidence < high]
            if bin_results:
                bin_correct = sum(1 for r in bin_results if r.correct)
                calibration[f"{low}-{high}%"] = {
                    'accuracy': bin_correct / len(bin_results),
                    'count': len(bin_results),
                    'avg_confidence': sum(r.confidence for r in bin_results) / len(bin_results)
                }
        
        return {
            'total_questions': total,
            'correct': correct,
            'accuracy': correct / total,
            'by_track': track_stats,
            'by_type': type_stats,
            'calibration': calibration,
            'avg_response_time_ms': sum(r.response_time_ms for r in self.results) / total
        }

    def print_summary(self):
        """Print evaluation summary"""
        summary = self.get_summary()
        if not summary:
            print("No results to summarize")
            return
        
        print(f"
{'='*70}")
        print(f"EVALUATION SUMMARY: {self.model_name.upper()}")
        print(f"{'='*70}")
        print(f"Total Questions: {summary['total_questions']}")
        print(f"Correct: {summary['correct']}")
        print(f"Accuracy: {summary['accuracy']:.2%}")
        print(f"Avg Response Time: {summary['avg_response_time_ms']:.0f}ms")
        
        if summary.get('by_track'):
            print(f"
{'─'*70}")
            print("BY TRACK:")
            for track, stats in sorted(summary['by_track'].items()):
                print(f"  {track.upper():6}: {stats['accuracy']:.1%} ({stats['count']} questions)")
        
        if summary.get('calibration'):
            print(f"
{'─'*70}")
            print("CALIBRATION ANALYSIS:")
            print("  Confidence Range | Accuracy | Sample Size")
            for conf_range, stats in sorted(summary['calibration'].items()):
                print(f"  {conf_range:17} | {stats['accuracy']:7.1%} | {stats['count']:4} questions")
        
        print(f"{'='*70}
")


class ClaudeEvaluator(ModelEvaluator):
    """Evaluate using Claude via Anthropic API"""

    def __init__(self, model_version: str = "claude-3-5-sonnet-20241022"):
        super().__init__("claude")
        self.model_version = model_version
        self.client = None
        
        # Initialize client if API key available
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            print("⚠️  Warning: ANTHROPIC_API_KEY not set. Claude evaluation will be simulated.")

    def evaluate(self, questions: List[Question], track: str, sample_size: Optional[int] = None) -> List[EvaluationResult]:
        """Evaluate questions using Claude API"""
        if sample_size:
            questions = questions[:sample_size]
        
        results = []
        
        for q in tqdm(questions, desc=f"Evaluating {track} with Claude"):
            if self.client:
                try:
                    prompt = self.format_prompt(q, track)
                    
                    start_time = time.time()
                    response = self.client.messages.create(
                        model=self.model_version,
                        max_tokens=500,
                        temperature=0.0,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    text = response.content[0].text
                    result = self.parse_response(text, q, track, response_time_ms)
                    results.append(result)
                    
                    # Rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"
❌ Error on question {q.id}: {e}")
                    # Add failed result
                    results.append(EvaluationResult(
                        question_id=q.id,
                        track=track,
                        question_type=q.question_type,
                        predicted="A",
                        correct=False,
                        confidence=0,
                        reasoning=f"API Error: {str(e)[:100]}",
                        response_time_ms=0
                    ))
            else:
                # Simulated evaluation for testing
                import random
                predicted = random.choice(['A', 'B', 'C', 'D'])
                results.append(EvaluationResult(
                    question_id=q.id,
                    track=track,
                    question_type=q.question_type,
                    predicted=predicted,
                    correct=(predicted == q.answer),
                    confidence=random.randint(50, 90),
                    reasoning="Simulated reasoning for testing",
                    response_time_ms=random.randint(500, 1500)
                ))
        
        self.results = results
        return results


class OpenAIEvaluator(ModelEvaluator):
    """Evaluate using OpenAI models (GPT-4, etc.)"""

    def __init__(self, model_version: str = "gpt-4o-mini-2024-07-18"):
        super().__init__("openai")
        self.model_version = model_version
        self.client = None
        
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
        else:
            print("⚠️  Warning: OPENAI_API_KEY not set. OpenAI evaluation will be simulated.")

    def evaluate(self, questions: List[Question], track: str, sample_size: Optional[int] = None) -> List[EvaluationResult]:
        """Evaluate questions using OpenAI API"""
        if sample_size:
            questions = questions[:sample_size]
        
        results = []
        
        for q in tqdm(questions, desc=f"Evaluating {track} with OpenAI"):
            if self.client:
                try:
                    prompt = self.format_prompt(q, track)
                    
                    start_time = time.time()
                    response = self.client.chat.completions.create(
                        model=self.model_version,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=500,
                        temperature=0.0
                    )
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    text = response.choices[0].message.content
                    result = self.parse_response(text, q, track, response_time_ms)
                    results.append(result)
                    
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    print(f"
❌ Error on question {q.id}: {e}")
                    results.append(EvaluationResult(
                        question_id=q.id,
                        track=track,
                        question_type=q.question_type,
                        predicted="A",
                        correct=False,
                        confidence=0,
                        reasoning=f"API Error: {str(e)[:100]}",
                        response_time_ms=0
                    ))
            else:
                # Simulated
                import random
                predicted = random.choice(['A', 'B', 'C', 'D'])
                results.append(EvaluationResult(
                    question_id=q.id,
                    track=track,
                    question_type=q.question_type,
                    predicted=predicted,
                    correct=(predicted == q.answer),
                    confidence=random.randint(50, 90),
                    reasoning="Simulated reasoning for testing",
                    response_time_ms=random.randint(400, 1200)
                ))
        
        self.results = results
        return results


class GeminiEvaluator(ModelEvaluator):
    """Evaluate using Google Gemini"""

    def __init__(self, model_version: str = "gemini-1.5-flash-latest"):
        super().__init__("gemini")
        self.model_version = model_version
        self.client = None
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(model_version)
        else:
            print("⚠️  Warning: GOOGLE_API_KEY not set. Gemini evaluation will be simulated.")

    def evaluate(self, questions: List[Question], track: str, sample_size: Optional[int] = None) -> List[EvaluationResult]:
        """Evaluate questions using Gemini API"""
        if sample_size:
            questions = questions[:sample_size]
        
        results = []
        
        for q in tqdm(questions, desc=f"Evaluating {track} with Gemini"):
            if self.client:
                try:
                    prompt = self.format_prompt(q, track)
                    
                    start_time = time.time()
                    response = self.client.generate_content(
                        prompt,
                        generation_config={
                            'temperature': 0.0,
                            'max_output_tokens': 500
                        }
                    )
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    text = response.text
                    result = self.parse_response(text, q, track, response_time_ms)
                    results.append(result)
                    
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    print(f"
❌ Error on question {q.id}: {e}")
                    results.append(EvaluationResult(
                        question_id=q.id,
                        track=track,
                        question_type=q.question_type,
                        predicted="A",
                        correct=False,
                        confidence=0,
                        reasoning=f"API Error: {str(e)[:100]}",
                        response_time_ms=0
                    ))
            else:
                # Simulated
                import random
                predicted = random.choice(['A', 'B', 'C', 'D'])
                results.append(EvaluationResult(
                    question_id=q.id,
                    track=track,
                    question_type=q.question_type,
                    predicted=predicted,
                    correct=(predicted == q.answer),
                    confidence=random.randint(50, 90),
                    reasoning="Simulated reasoning for testing",
                    response_time_ms=random.randint(300, 1000)
                ))
        
        self.results = results
        return results


def load_questions(track_dir: str) -> List[Question]:
    """Load MC questions from CSV file"""
    import csv
    
    questions = []
    csv_path = Path(track_dir)
    
    if not csv_path.exists():
        print(f"❌ Directory not found: {csv_path}")
        return []
    
    # Find CSV file in directory
    csv_files = list(csv_path.glob("*.csv"))
    if not csv_files:
        print(f"❌ No CSV files found in {csv_path}")
        return []
    
    # Prefer files with "new" or "mc" in name, otherwise take first
    csv_file = None
    for f in csv_files:
        if 'new' in f.name.lower() or 'mc' in f.name.lower():
            csv_file = f
            break
    if not csv_file:
        csv_file = csv_files[0]
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Handle different CSV formats
                q_id = row.get('id', row.get('question_id', ''))
                q_type = row.get('question_type', row.get('type', ''))
                q_text = row.get('question', row.get('text', ''))
                answer = row.get('answer', row.get('correct_answer', ''))
                
                # Extract choices (handle different column names)
                choices = []
                for letter in ['A', 'B', 'C', 'D']:
                    choice = row.get(letter, '')
                    choices.append(choice)
                
                questions.append(Question(
                    id=q_id,
                    question_type=q_type,
                    question=q_text,
                    choices=choices,
                    answer=answer
                ))
        
        print(f"✅ Loaded {len(questions)} questions from {csv_file.name}")
        
    except Exception as e:
        print(f"❌ Error loading {csv_file}: {e}")
        return []
    
    return questions


def main():
    """Main evaluation script"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Evaluate Trinity Cognitive Probes on LLMs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/evaluate.py --model claude --track thlp --sample 100
  python scripts/evaluate.py --model openai --track all --sample 1000
  python scripts/evaluate.py --model gemini --track ttm,tscp --sample 50
        """
    )
    
    parser.add_argument('--model', required=True, 
                       choices=['claude', 'openai', 'gemini', 'all'],
                       help='Model to evaluate')
    parser.add_argument('--track', default='all',
                       help='Track(s) to evaluate: thlp, ttm, tagp, tefb, tscp, or all (comma-separated for multiple)')
    parser.add_argument('--sample', type=int, default=None,
                       help='Number of questions to sample per track (default: all)')
    parser.add_argument('--output-dir', default='runs',
                       help='Output directory for results (default: runs)')
    
    args = parser.parse_args()
    
    # Parse tracks
    if args.track == 'all':
        tracks_to_run = ['thlp', 'ttm', 'tagp', 'tefb', 'tscp']
    else:
        tracks_to_run = [t.strip().lower() for t in args.track.split(',')]
    
    # Parse models
    if args.model == 'all':
        models_to_run = ['claude', 'openai', 'gemini']
    else:
        models_to_run = [args.model]
    
    base_dir = Path(__file__).parent.parent / "data"
    
    # Run evaluations
    for model_name in models_to_run:
        print(f"
{'='*70}")
        print(f"🚀 STARTING EVALUATION: {model_name.upper()}")
        print(f"Tracks: {', '.join(tracks_to_run)}")
        if args.sample:
            print(f"Sample size: {args.sample} questions per track")
        print(f"{'='*70}
")
        
        # Create evaluator
        evaluators = {
            'claude': ClaudeEvaluator,
            'openai': OpenAIEvaluator,
            'gemini': GeminiEvaluator
        }
        
        evaluator = evaluators[model_name]()
        
        # Run for each track
        for track in tracks_to_run:
            track_dir = base_dir / track
            questions = load_questions(track_dir)
            
            if not questions:
                print(f"⚠️  Skipping {track}: no questions loaded")
                continue
            
            # Evaluate
            evaluator.evaluate(questions, track, sample_size=args.sample)
            
            # Save results for this track
            output_dir = Path(args.output_dir) / model_name
            evaluator.save_results(output_dir, track)
        
        # Save combined results if multiple tracks
        if len(tracks_to_run) > 1:
            all_output_dir = Path(args.output_dir) / model_name
            evaluator.save_results(all_output_dir, "combined")
    
    print("
✅ All evaluations complete!")


if __name__ == "__main__":
    main()
