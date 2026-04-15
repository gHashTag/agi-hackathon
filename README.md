# Measuring Progress Toward AGI - Cognitive Abilities

Google DeepMind x Kaggle Hackathon 2026

## Overview

This repository contains evaluation scripts and probes for the "Measuring Progress Toward AGI: A Cognitive Framework" hackathon.

## 5 Cognitive Tracks

| Track | Description | URL | Questions | Status |
|-------|-------------|-----|----------|--------|
| **THLP** | Pattern learning, belief update, rule induction | [THLP](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-thlp-mc) | ✅ Ready |
| **TTM** | Metacognitive Calibration | [TTM](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-ttm-mc) | ✅ Ready |
| **TAGP** | Selective filtering, sustained attention, attention shifting | [TAGP](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tagp-mc) | ⚠️ Missing description |
| **TEFB** | Multi-step planning, working memory, cognitive flexibility | [TEFB](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tefb-mc) | ✅ Ready |
| **TSCP** | Theory of Mind, pragmatic inference, social norms | [TSCP](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tscp-mc) | ✅ Ready |

**Total Questions:** 65,133 MC questions

## Known Issues

1. **Missing Descriptions:** THLP and TAGP have empty "About Dataset" descriptions
2. **Question Count Discrepancies:**
   - TTM: 733 (About) vs 4,931 (README) — discrepancy of -4,198
   - TEFB: 1,805 (About) vs 21,081 (README) — discrepancy of -19,276
   - TSCP: 1,584 (About) vs 2,839 (README) — discrepancy of -1,255

3. **License:** All tracks show CC0, but TSCP About mentions MIT

## Project Structure

```
agi-hackathon/
├── README.md
├── data/                      # Downloaded Kaggle datasets
│   ├── thlp/
│   ├── ttm/
│   ├── tagp/
│   ├── tefb/
│   └── tscp/
├── runs/                       # Evaluation runs
│   ├── claude/
│   ├── gemini/
│   └── openai/
├── prompts/                    # Evaluation prompts
│   ├── system_prompts.md
│   └── track_prompts.md
└── scripts/                    # Utility scripts
    ├── download_data.sh
    └── evaluate.py
```

## Quick Start

```bash
# Download data
python scripts/download_data.py

# Run evaluation
python scripts/evaluate.py --model claude --track all
```

## Sources

- [DeepMind AGI Framework Paper](https://arxiv.org/abs/XXXXX)
- [Kaggle Hackathon](https://www.kaggle.com/competitions/google-deepmind/measuring-progress-toward-agi-cognitive-abilities)
- [Trinity Cognitive Probes GitHub](https://github.com/browseros-ai/trinity-cognitive-probes)
