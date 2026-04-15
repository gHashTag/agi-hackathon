# AGI Hackathon 2026

Google DeepMind x Kaggle "Measuring Progress Toward AGI: A Cognitive Framework" Hackathon 2026

## Status: 85% Ready for Production

| Component | Status | Details |
|-----------|---------|---------|
| Adversarial Datasets | ✅ Complete | 2,861 questions across 5 tracks |
| Notebooks | ✅ Fixed | All 5 notebooks JSON-valid and ready |
| Kaggle Datasets | ✅ Uploaded | All 5 adversarial datasets on Kaggle |
| Inference Script | ✅ Created | Ready to run with API keys |
| Real Predictions | ⏳ Pending | Requires API keys for model inference |
| Final Submission | ⏳ Pending | Dummy submission created |

---

## Overview

This repository contains adversarial datasets and evaluation resources for the AGI Hackathon 2026. We focus on evaluating 5 cognitive tracks from the Trinity Cognitive Probes framework using **adversarial** questions that test true cognitive capabilities rather than memorization.

## 5 Cognitive Tracks (Adversarial)

| Track | Full Name | Questions | Expected Accuracy | Kaggle Dataset |
|-------|-----------|-----------|-------------------|-----------------|
| **THLP** | Trinity Hierarchical Learning Pattern | 274 | 25-40% | [playra/trinity-thlp-adversarial](https://www.kaggle.com/datasets/playra/trinity-thlp-adversarial) |
| **TTM** | Trinity Metacognitive | 199 | 10-25% | [playra/trinity-ttm-physics-enhanced](https://www.kaggle.com/datasets/playra/trinity-ttm-physics-enhanced) |
| **TAGP** | Trinity Attention Grid Pattern | 851 | 20-35% | [playra/trinity-tagp-adversarial](https://www.kaggle.com/datasets/playra/trinity-tagp-adversarial) |
| **TEFB** | Trinity Executive Function Battery | 1,512 | 50-70% | [playra/trinity-tefb-cleaned](https://www.kaggle.com/datasets/playra/trinity-tefb-cleaned) |
| **TSCP** | Trinity Social Cognition Protocol | 25 | 60-80% | [playra/trinity-tscp-cleaned](https://www.kaggle.com/datasets/playra/trinity-tscp-cleaned) |

**Total: 2,861 Adversarial Questions**

---

## Quick Start

```bash
# Clone repository
git clone https://github.com/gHashTag/agi-hackathon.git
cd agi-hackathon

# Explore adversarial datasets
ls kaggle/data/extra/
```

---

## Running Inference

### Prerequisites

Set your API keys as environment variables:

```bash
export ANTHROPIC_API_KEY="your-key-here"   # Claude
export OPENAI_API_KEY="your-key-here"       # GPT-4o
export GOOGLE_API_KEY="your-key-here"        # Gemini
```

### Run Inference

```bash
# Run on all tracks with GPT-4o
python3 scripts/inference.py --model gpt-4o --track all --output inference_results

# Run on single track with Claude
python3 scripts/inference.py --model claude --track thlp --output results

# Test with sample (first 10 questions)
python3 scripts/inference.py --model gpt-4o --track all --sample 10
```

### Available Models

| Model | API | Command |
|--------|------|---------|
| Claude 3.5 Sonnet | Anthropic | `--model claude` |
| GPT-4o | OpenAI | `--model gpt-4o` |
| Gemini 1.5 Flash | Google | `--model gemini` |

---

## Kaggle Submission

### Current Status

A dummy submission file exists at `kaggle/submission.csv` with 2,711 predictions (all "A").

### For Real Submission

1. **Run inference** with valid API keys:
   ```bash
   python3 scripts/inference.py --model gpt-4o --track all --output inference_results
   ```

2. **Validate predictions**:
   ```bash
   head inference_results/submission.csv
   ```

3. **Upload to Kaggle**:
   - Go to the AGI Hackathon competition page
   - Click "Submit Predictions"
   - Upload your `submission.csv`

---

## Datasets

### Adversarial Datasets (for evaluation)

| File | Questions | Description |
|------|-----------|-------------|
| `kaggle/data/extra/thlp_mc_aggressive.csv` | 274 | Pattern-breaking THLP questions |
| `kaggle/data/extra/ttm_physics_mc.csv` | 199 | Physics-enhanced TTM questions |
| `kaggle/data/tagp_mc_aggressive.csv` | 851 | Adversarial TAGP questions |
| `kaggle/data/extra/tefb_mc_cleaned.csv` | 1,512 | Cleaned TEFB questions |
| `kaggle/data/extra/tscp_mc_cleaned.csv` | 25 | Cleaned TSCP questions |

### Original Datasets (for reference)

| File | Questions | Status |
|------|-----------|---------|
| `kaggle/data/thlp_mc_fixed.csv` | 19,680 | Fixed UTF-8 issues |
| `kaggle/data/ttm_mc_fixed.csv` | 2,482 | Artificial structure (see audit) |
| `kaggle/data/tagp_mc_fixed.csv` | 17,600 | Fixed encoding |
| `kaggle/data/tefb_mc_fixed.csv` | 21,080 | Normalized answers |
| `kaggle/data/tscp_mc_fixed.csv` | 2,839 | Fixed delimiters |

---

## Key Findings

### TTM Dataset Audit

The original TTM dataset had **artificial structure**:
- 816 rows = 33 unique questions × 4 variants
- Each question appeared 4 times with different correct answers
- This gave 100% accuracy for pattern-matching models

**Solution:** Created adversarial physics-enhanced dataset (199 questions) with realistic structure. Expected accuracy: 10-25%.

---

## Documentation

- `kaggle/STATUS.md` - Dataset status and quality
- `kaggle/BENCHMARK_MODELS.md` - Model benchmarking guide
- `kaggle/KAGGLE_SUBMISSION_GUIDE.md` - Submission instructions
- `kaggle/KAGGLE_FIXES_REPORT.md` - Dataset fixes applied
- `scripts/inference.py` - Main inference script

---

## Notebooks

All notebooks have been fixed and are JSON-valid:

| Notebook | Track | Status |
|----------|-------|--------|
| `notebooks/thlp_mc_benchmark.ipynb` | THLP | ✅ Valid |
| `notebooks/ttm_mc_benchmark.ipynb` | TTM | ✅ Valid |
| `notebooks/tagp_mc_benchmark.ipynb` | TAGP | ✅ Valid |
| `notebooks/tefb_mc_benchmark.ipynb` | TEFB | ✅ Valid |
| `notebooks/tscp_mc_benchmark.ipynb` | TSCP | ✅ Valid |

---

## Citation

```bibtex
@online{AGI Hackathon 2026},
  title={Measuring Progress Toward AGI: A Cognitive Framework Benchmark with Adversarial Datasets},
  author={Vasilev, Dmitrii},
  booktitle={Kaggle: The World's AI Proving Ground},
  year={2026},
  publisher={Google DeepMind},
  url={https://github.com/gHashTag/agi-hackathon}
}
```

## License

MIT License
