# Kaggle Datasets for AGI Hackathon 2026

This directory contains the Trinity Cognitive Probes datasets prepared for the AGI Hackathon 2026.

## Datasets

### THLP - Pattern Learning
- **File**: `thlp_mc_fixed.csv`
- **Questions**: 19,680
- **Focus**: Pattern recognition, inductive reasoning, rule learning
- **Kaggle**: [trinity-cognitive-probes-thlp-mc](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-thlp-mc)

### TTM - Metacognitive Calibration
- **File**: `ttm_mc_fixed.csv`
- **Questions**: 2,482
- **Focus**: Confidence calibration, error detection, meta-learning
- **Kaggle**: [trinity-cognitive-probes-ttm-mc](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-ttm-mc)

### TAGP - Attention Control
- **File**: `tagp_mc_fixed.csv`
- **Questions**: 17,600
- **Focus**: Selective attention, sustained focus, attention shifting
- **Kaggle**: [trinity-cognitive-probes-tagp-mc](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tagp-mc)

### TEFB - Executive Functions
- **File**: `tefb_mc_fixed.csv`
- **Questions**: 21,080
- **Focus**: Multi-step planning, working memory, cognitive flexibility
- **Kaggle**: [trinity-cognitive-probes-tefb-mc](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tefb-mc)

### TSCP - Social Cognition
- **File**: `tscp_mc_fixed.csv`
- **Questions**: 2,839
- **Focus**: Theory of Mind, pragmatic inference, social norms
- **Kaggle**: [trinity-cognitive-probes-tscp-mc](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tscp-mc)

## CSV Format

All CSV files follow this structure:

| Column | Description | Example |
|--------|-------------|----------|
| id | Unique question identifier | thlp_00001 |
| question_type | Cognitive sub-type | pattern_completion |
| question | Question text | What comes next in the pattern? |
| A | Choice A | Option A text |
| B | Choice B | Option B text |
| C | Choice C | Option C text |
| D | Choice D | Option D text |
| answer | Correct answer | B |

## Data Quality

All datasets have been fixed and validated:
- UTF-8 encoding
- Standardized CSV delimiters
- Normalized answer format
- Validated choice counts (4 per question)
- Removed duplicates and corrupted rows

See `KAGGLE_FIXES_REPORT.md` for detailed fix documentation.

## Using the Datasets

### For Evaluation

Use the evaluation framework: https://github.com/gHashTag/agi-hackathon-eval

```bash
git clone https://github.com/gHashTag/agi-hackathon-eval.git
cd agi-hackathon-eval
python3 scripts/evaluate.py --model claude --track thlp --sample 1000
```

### For Analysis

Load directly into Python:

```python
import pandas as pd

df = pd.read_csv('kaggle/data/thlp_mc_fixed.csv')
print(f"Loaded {len(df)} questions")
print(df.head())
```

## Status

See `STATUS.md` for current dataset status and quality metrics.

## Scripts

- `scripts/fix_kaggle_datasets.py` - Apply fixes to raw datasets
- `scripts/browser_control.py` - Browser automation for Kaggle downloads
- `scripts/upload_mc_datasets.py` - Upload to Kaggle (prepared)
- `scripts/upload_mc_datasets_fixed.py` - Upload fixed datasets (prepared)

## Citation

```bibtex
@online{Trinity Cognitive Probes 2026},
  title={Trinity Cognitive Probes: A Framework for Measuring Progress Toward AGI},
  author={{Google DeepMind}},
  year={2026},
  url={https://www.kaggle.com/datasets/playra/trinity-cognitive-probes}
}
```
