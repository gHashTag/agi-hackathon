# Trinity Cognitive Probes - AGI Hackathon Benchmark

**Authors:** AGI Hackathon Team
**Date:** April 15, 2026
**Competition:** Measuring Progress Toward AGI (Kaggle Benchmarks)

## Overview

This benchmark evaluates Large Language Models across five cognitive faculties essential for AGI:
- **Learning (THLP)** - Pattern acquisition and rule induction
- **Metacognition (TTM)** - Confidence calibration and error detection
- **Attention (TAGP)** - Selective focus and information filtering
- **Executive Functions (TEFB)** - Multi-step planning and cognitive flexibility
- **Social Cognition (TSCP)** - Theory of Mind and pragmatic inference

## Benchmark Goals

1. Isolate cognitive abilities beyond surface knowledge
2. Resist shortcut exploitation through memorization
3. Provide detailed error analysis per capability
4. Enable reproducible evaluation of frontier models

## Dataset Description

- **Total Questions:** 1,860 adversarial questions
- **Question Types:** Multiple choice (A/B/C/D)
- **Adversarial Strategies:** Negative constraints, paraphrasing, answer scrambling
- **Difficulty Calibration:** Target 20-40% accuracy across all tracks

## Task Definitions

### THLP - Learning

Evaluate model's ability to:
- Induce rules from few-shot examples
- Detect patterns in sequences
- Generalize patterns to novel cases
- Recognize exceptions to induced rules

**Question Types:**
- Pattern completion (inductive reasoning)
- Rule application (deductive reasoning)
- Analogical reasoning

### TTM - Metacognition

Evaluate model's ability to:
- Calibrate confidence accurately
- Detect when uncertain
- Recognize own knowledge boundaries
- Adjust strategies based on difficulty

**Question Types:**
- Confidence estimation
- Error detection scenarios
- Knowledge boundary queries
- Meta-learning tasks

### TAGP - Attention

Evaluate model's ability to:
- Maintain focus on relevant information
- Ignore distracting elements
- Shift attention appropriately
- Sustain attention through complex tasks

**Question Types:**
- Selective filtering tasks
- Distractor detection
- Attention shifting scenarios
- Sustained attention benchmarks

### TEFB - Executive Functions

Evaluate model's ability to:
- Plan multi-step solutions
- Maintain working memory
- Adapt to changing constraints
- Switch strategies when plans fail

**Question Types:**
- Planning and sequencing
- Working memory tasks
- Cognitive flexibility scenarios
- Inhibition and control

### TSCP - Social Cognition

Evaluate model's ability to:
- Infer mental states
- Understand indirect communication
- Navigate social norms
- Interpret pragmatic meaning

**Question Types:**
- Theory of Mind tasks
- Pragmatic inference
- Social norms understanding
- Indirect communication interpretation

## Scoring

Each model receives a composite score based on:
- **Accuracy (60%)** - Correct answer selection
- **Calibration (20%)** - Confidence alignment with accuracy
- **Reasoning Quality (20%)** - Depth and relevance of explanations

## Citation

If you use this benchmark in your research, please cite:

```
AGI Hackathon Team. Measuring Progress Toward AGI: A Comprehensive Cognitive Framework. Kaggle Benchmarks, 2024.
```
