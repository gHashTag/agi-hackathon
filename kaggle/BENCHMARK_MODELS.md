# Model Benchmarking Guide

## Supported Models

| Model | Provider | API Key | Cost | Notes |
|-------|----------|-----------|------|-------|
| Claude 3.5 Sonnet | Anthropic | ANTHROPIC_API_KEY | ~$3.00/1K Q | Best for reasoning |
| GPT-4o | OpenAI | OPENAI_API_KEY | ~$0.15/1K Q | Fast, cost-effective |
| Gemini 1.5 Flash | Google | GOOGLE_API_KEY | ~$0.08/1K Q | Cheapest option |
| GLM-5 | Zhipu AI | ZHIPU_API_KEY | Experimental | Chinese model |

## Evaluation Framework

Use the evaluation framework at: https://github.com/gHashTag/agi-hackathon-eval

```bash
# Install dependencies
pip install -r agi-hackathon-eval/requirements.txt

# Run evaluation
python3 agi-hackathon-eval/scripts/evaluate.py --model claude --track all --sample 100
```

## Scoring System

Total Score = Correctness (60%) + Calibration (20%) + Quality (20%)

### Correctness (60%)

Simple accuracy: correct_answers / total_questions

### Calibration (20%)

Confidence calibration score based on:
- Brier score (confidence accuracy)
- Expected Calibration Error (ECE)
- Reliability diagrams

### Quality (20%)

Based on reasoning depth and explanation quality:
- Pattern recognition (THLP)
- Metacognitive awareness (TTM)
- Attention control (TAGP)
- Planning structure (TEFB)
- Social reasoning (TSCP)

## Benchmarks to Beat

### Human Baselines

| Track | Human Average | Target |
|-------|--------------|--------|
| THLP | 78% | 80%+ |
| TTM | 85% | 90%+ |
| TAGP | 72% | 75%+ |
| TEFB | 68% | 72%+ |
| TSCP | 74% | 78%+ |

### Current SOTA

| Model | THLP | TTM | TAGP | TEFB | TSCP |
|-------|------|-----|------|------|------|
| Claude 3.5 Sonnet | TBD | TBD | TBD | TBD | TBD |
| GPT-4o | TBD | TBD | TBD | TBD | TBD |
| Gemini 1.5 Flash | TBD | TBD | TBD | TBD | TBD |

## Running Benchmarks

```bash
# Full evaluation (all tracks, all questions)
python3 evaluate.py --model claude --track all

# Sample evaluation (for testing)
python3 evaluate.py --model claude --track thlp --sample 100

# Compare models (same questions)
python3 evaluate.py --model claude --track thlp --sample 100
python3 evaluate.py --model gpt-4 --track thlp --sample 100
python3 evaluate.py --model gemini --track thlp --sample 100
```

## Analyzing Results

```bash
# Compare model performances
python3 scripts/analyze_results.py --runs runs/claude runs/openai runs/gemini
```

## Reporting

Report format for hackathon submission:
- Model name and version
- Per-track accuracy
- Calibration metrics
- Qualitative analysis of failures
- Training/fine-tuning details (if any)
