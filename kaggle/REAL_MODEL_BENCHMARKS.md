# Real Model Benchmarks

This document contains actual benchmark results from real models on Trinity Cognitive Probes datasets.

## How to Run Benchmarks

1. Set up evaluation environment:
```bash
git clone https://github.com/gHashTag/agi-hackathon-eval.git
cd agi-hackathon-eval
pip install -r requirements.txt
```

2. Set API keys:
```bash
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
export ZHIPU_API_KEY="your-key"
```

3. Run evaluation:
```bash
# Single model, single track
python3 scripts/evaluate.py --model claude --track thlp --sample 1000

# Full evaluation (all tracks)
python3 scripts/evaluate.py --model claude --track all
```

## Expected Results Format

Results are saved in `runs/` directory as JSON:

```json
{
  "model": "claude",
  "track": "thlp",
  "timestamp": "20260415_120000",
  "total_questions": 1000,
  "summary": {
    "accuracy": 0.723,
    "correct": 723,
    "total": 1000,
    "track_stats": {
      "thlp": {"accuracy": 0.723, "count": 1000}
    },
    "calibration": {
      "0-30": {"accuracy": 0.45, "count": 200},
      "30-50": {"accuracy": 0.68, "count": 300},
      "50-70": {"accuracy": 0.82, "count": 400},
      "70-90": {"accuracy": 0.91, "count": 100}
    }
  }
}
```

## Recording Your Benchmarks

To add your results to this document, create a PR with:

1. Run evaluation on all 5 tracks
2. Save results JSON
3. Update this section with your findings

---

## Benchmark Results

### Claude 3.5 Sonnet

| Track | Accuracy | Calibration | Sample Size | Date |
|-------|----------|-------------|-------------|-------|
| THLP | TBD | TBD | TBD | TBD |
| TTM | TBD | TBD | TBD | TBD |
| TAGP | TBD | TBD | TBD | TBD |
| TEFB | TBD | TBD | TBD | TBD |
| TSCP | TBD | TBD | TBD | TBD |

### GPT-4o

| Track | Accuracy | Calibration | Sample Size | Date |
|-------|----------|-------------|-------------|-------|
| THLP | TBD | TBD | TBD | TBD |
| TTM | TBD | TBD | TBD | TBD |
| TAGP | TBD | TBD | TBD | TBD |
| TEFB | TBD | TBD | TBD | TBD |
| TSCP | TBD | TBD | TBD | TBD |

### Gemini 1.5 Flash

| Track | Accuracy | Calibration | Sample Size | Date |
|-------|----------|-------------|-------------|-------|
| THLP | TBD | TBD | TBD | TBD |
| TTM | TBD | TBD | TBD | TBD |
| TAGP | TBD | TBD | TBD | TBD |
| TEFB | TBD | TBD | TBD | TBD |
| TSCP | TBD | TBD | TBD | TBD |

### GLM-5 (Experimental)

| Track | Accuracy | Calibration | Sample Size | Date |
|-------|----------|-------------|-------------|-------|
| THLP | TBD | TBD | TBD | TBD |
| TTM | TBD | TBD | TBD | TBD |
| TAGP | TBD | TBD | TBD | TBD |
| TEFB | TBD | TBD | TBD | TBD |
| TSCP | TBD | TBD | TBD | TBD |
