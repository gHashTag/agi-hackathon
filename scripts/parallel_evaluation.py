#!/usr/bin/env python3
"""
Parallel Evaluation Module for AGI Hackathon
Implements concurrent API calls with rate limiting and progress tracking.

Author: AGI Hackathon Team
Date: 2026-04-15

Features:
- ThreadPoolExecutor for parallel API calls
- Per-API rate limiting
- Real-time progress tracking with ETA
- Graceful shutdown on errors
- Failed question tracking
"""

import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json


@dataclass
class ParallelConfig:
    """Configuration for parallel evaluation"""
    max_workers: int = 5
    rate_limit_per_minute: int = 60
    batch_size: int = 10
    timeout_seconds: int = 120
    enable_progress: bool = True


@dataclass
class EvalProgress:
    """Track evaluation progress"""
    total: int = 0
    completed: int = 0
    failed: int = 0
    start_time: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

    @property
    def elapsed(self) -> float:
        return time.time() - self.start_time

    @property
    def percent(self) -> float:
        return (self.completed / self.total * 100) if self.total > 0 else 0

    @property
    def eta(self) -> float:
        if self.completed == 0:
            return 0
        rate = self.elapsed / self.completed
        remaining = self.total - self.completed
        return rate * remaining

    @property
    def rate(self) -> float:
        elapsed = self.elapsed
        return self.completed / elapsed if elapsed > 0 else 0


class RateLimiter:
    """Token bucket rate limiter for API calls"""

    def __init__(self, max_calls: int, time_window: float = 60.0):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = threading.Lock()

    def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Acquire permission to make an API call.

        Args:
            timeout: Maximum time to wait (None = wait indefinitely)

        Returns:
            True if permission granted, False if timeout
        """
        with self.lock:
            now = time.time()

            # Remove old calls
            self.calls = [t for t in self.calls if now - t < self.time_window]

            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True

            if timeout is None:
                # Wait until slot available
                oldest = self.calls[0]
                wait_time = self.time_window - (now - oldest) + 0.01
                time.sleep(wait_time)
                self.calls.append(now)
                return True

            # Check if we can wait within timeout
            oldest = self.calls[0]
            wait_time = self.time_window - (now - oldest) + 0.01

            if wait_time <= timeout:
                time.sleep(wait_time)
                self.calls.append(now)
                return True

            return False


class ProgressTracker:
    """Track and display evaluation progress"""

    def __init__(self, total: int, show_bar: bool = True):
        self.total = total
        self.completed = 0
        self.failed = 0
        self.show_bar = show_bar
        self.start_time = time.time()
        self.lock = threading.Lock()
        self.last_bar_length = 0

    def update(self, success: bool = True):
        """Update progress (thread-safe)"""
        with self.lock:
            if success:
                self.completed += 1
            else:
                self.failed += 1
            self._display()

    def _display(self):
        """Display progress bar"""
        if not self.show_bar:
            return

        percent = self.completed / self.total * 100 if self.total > 0 else 0
        elapsed = time.time() - self.start_time
        rate = self.completed / elapsed if elapsed > 0 else 0

        # Progress bar
        bar_width = 40
        filled = int(bar_width * self.completed / self.total)
        bar = '█' * filled + '░' * (bar_width - filled)

        # ETA
        if self.completed > 0 and self.completed < self.total:
            eta = (self.total - self.completed) / rate
            eta_str = str(timedelta(seconds=int(eta)))
        else:
            eta_str = "--:--:--"

        # Build output
        output = f"\r[{bar}] {percent:.1f}% | {self.completed}/{self.total} | {rate:.2f} q/s | ETA: {eta_str}"

        if self.failed > 0:
            output += f" | ❌ {self.failed} failed"

        # Clear previous line
        if self.last_bar_length > 0:
            output += ' ' * max(0, self.last_bar_length - len(output))

        print(output, end='', flush=True)
        self.last_bar_length = len(output)

    def finish(self):
        """Display final summary"""
        if self.show_bar:
            print()  # New line after progress bar

        elapsed = time.time() - self.start_time
        rate = self.completed / elapsed if elapsed > 0 else 0

        print(f"✅ Completed: {self.completed}/{self.total} ({self.completed / self.total * 100:.1f}%)")
        print(f"   Time: {timedelta(seconds=int(elapsed))}")
        print(f"   Rate: {rate:.2f} questions/second")
        if self.failed > 0:
            print(f"   Failed: {self.failed}")


def parallel_evaluate(
    questions: List,
    evaluate_fn: Callable,
    config: ParallelConfig = None,
    model_name: str = "model",
    track: str = "unknown"
) -> List[Dict]:
    """
    Evaluate questions in parallel with rate limiting.

    Args:
        questions: List of questions to evaluate
        evaluate_fn: Function that takes a question and returns result
        config: Parallel configuration
        model_name: Name of model (for logging)
        track: Track name (for logging)

    Returns:
        List of evaluation results
    """
    if config is None:
        config = ParallelConfig()

    # Setup
    rate_limiter = RateLimiter(
        max_calls=config.rate_limit_per_minute,
        time_window=60.0
    )
    progress = ProgressTracker(len(questions), show_bar=config.enable_progress)

    # Track results
    results = []
    failed_questions = []

    # Wrapper function for each question
    def evaluate_single(q):
        # Acquire rate limit
        if not rate_limiter.acquire(timeout=config.timeout_seconds):
            raise TimeoutError("Rate limiter timeout")

        # Evaluate
        try:
            result = evaluate_fn(q)
            progress.update(success=True)
            return result
        except Exception as e:
            progress.update(success=False)
            return {
                'question_id': getattr(q, 'id', 'unknown'),
                'error': str(e),
                'success': False
            }

    # Evaluate in parallel
    print(f"\n🚀 Starting parallel evaluation ({config.max_workers} workers)")
    print(f"   Track: {track}")
    print(f"   Questions: {len(questions)}")
    print(f"   Rate limit: {config.rate_limit_per_minute} calls/min")
    print()

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        # Submit all tasks
        future_to_q = {
            executor.submit(evaluate_single, q): q
            for q in questions
        }

        # Collect results as they complete
        for future in as_completed(future_to_q):
            q = future_to_q[future]
            try:
                result = future.result(timeout=config.timeout_seconds)
                if result.get('success', True):
                    results.append(result)
                else:
                    failed_questions.append(result)
            except Exception as e:
                failed_questions.append({
                    'question_id': getattr(q, 'id', 'unknown'),
                    'error': f"Timeout: {str(e)}",
                    'success': False
                })
                progress.update(success=False)

    # Finish progress display
    progress.finish()

    elapsed = time.time() - start_time
    print(f"📊 Parallel evaluation complete in {timedelta(seconds=int(elapsed))}")

    return results, failed_questions


def parallel_evaluate_batches(
    questions: List,
    evaluate_fn: Callable,
    batch_fn: Callable,
    config: ParallelConfig = None,
    model_name: str = "model",
    track: str = "unknown"
) -> List[Dict]:
    """
    Evaluate questions in parallel with batch processing.

    Args:
        questions: List of questions to evaluate
        evaluate_fn: Function that takes a question and returns result
        batch_fn: Function to batch multiple questions
        config: Parallel configuration
        model_name: Name of model
        track: Track name

    Returns:
        List of evaluation results
    """
    if config is None:
        config = ParallelConfig()

    # Split into batches
    batches = [
        questions[i:i + config.batch_size]
        for i in range(0, len(questions), config.batch_size)
    ]

    print(f"\n🚀 Starting batched parallel evaluation")
    print(f"   Track: {track}")
    print(f"   Questions: {len(questions)}")
    print(f"   Batch size: {config.batch_size}")
    print(f"   Number of batches: {len(batches)}")
    print()

    results = []
    failed_questions = []
    progress = ProgressTracker(len(batches), show_bar=config.enable_progress)

    def evaluate_batch(batch):
        """Evaluate a batch of questions"""
        try:
            batch_results = batch_fn(batch, evaluate_fn)
            progress.update(success=True)
            return batch_results
        except Exception as e:
            progress.update(success=False)
            return []

    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        future_to_batch = {
            executor.submit(evaluate_batch, batch): i
            for i, batch in enumerate(batches)
        }

        for future in as_completed(future_to_batch):
            batch_idx = future_to_batch[future]
            try:
                batch_results = future.result(timeout=config.timeout_seconds)
                results.extend(batch_results)
            except Exception as e:
                failed_questions.append({
                    'batch_id': batch_idx,
                    'error': str(e),
                    'success': False
                })

    progress.finish()

    print(f"📊 Batch evaluation complete: {len(results)} results from {len(batches)} batches")

    return results, failed_questions


class ParallelModelEvaluator:
    """Parallel evaluator wrapper for existing ModelEvaluator classes"""

    def __init__(self, evaluator_class, model_name: str, config: ParallelConfig = None):
        """
        Initialize parallel evaluator.

        Args:
            evaluator_class: ModelEvaluator class to wrap
            model_name: Name of the model
            config: Parallel configuration
        """
        self.evaluator_class = evaluator_class
        self.model_name = model_name
        self.config = config or ParallelConfig()

    def evaluate(
        self,
        questions: List,
        track: str,
        sample_size: Optional[int] = None
    ) -> tuple:
        """
        Evaluate questions in parallel.

        Args:
            questions: List of Question objects
            track: Track name
            sample_size: Optional sample size

        Returns:
            Tuple of (results, failed_questions)
        """
        # Limit sample size
        if sample_size:
            questions = questions[:sample_size]

        # Create evaluator instance (one per worker thread)
        def evaluate_single(q):
            # Create new evaluator instance for this thread
            evaluator = self.evaluator_class(self.model_name)
            return evaluator.evaluate([q], track)[0]

        # Run parallel evaluation
        results, failed = parallel_evaluate(
            questions,
            evaluate_single,
            self.config,
            self.model_name,
            track
        )

        return results, failed


def main():
    """Main entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Parallel evaluation module")
    parser.add_argument('--workers', type=int, default=5,
                       help='Number of parallel workers')
    parser.add_argument('--rate-limit', type=int, default=60,
                       help='Rate limit (calls per minute)')
    parser.add_argument('--test', action='store_true',
                       help='Run test evaluation')

    args = parser.parse_args()

    if args.test:
        # Test with dummy function
        def dummy_evaluate(q):
            time.sleep(0.1)  # Simulate API call
            return {
                'question_id': q,
                'success': True,
                'answer': 'A',
                'confidence': 85
            }

        questions = [f"q_{i}" for i in range(50)]

        config = ParallelConfig(
            max_workers=args.workers,
            rate_limit_per_minute=args.rate_limit,
            enable_progress=True
        )

        results, failed = parallel_evaluate(
            questions,
            dummy_evaluate,
            config,
            model_name="test_model",
            track="test_track"
        )

        print(f"\n✅ Test complete: {len(results)} results, {len(failed)} failed")


if __name__ == "__main__":
    main()
