# Trinity Cognitive Probes Adversarial Benchmarks

## Overview

This package contains 5 adversarial benchmarks testing true cognitive capabilities
rather than memorization. Total: 2,861 questions.

## Tracks

| Track | Name | Questions | Expected Accuracy | Dataset |
|--------|------|-----------|------------------|----------|
| THLP | Trinity Hierarchical Learning Pattern | 274 | 25-40% | [playra/trinity-thlp-adversarial](https://www.kaggle.com/datasets/playra/trinity-thlp-adversarial) |
| TTM | Trinity Metacognitive | 199 | 10-25% | [playra/trinity-ttm-physics-enhanced](https://www.kaggle.com/datasets/playra/trinity-ttm-physics-enhanced) |
| TAGP | Trinity Attention Grid Pattern | 851 | 20-35% | [playra/trinity-tagp-adversarial](https://www.kaggle.com/datasets/playra/trinity-tagp-adversarial) |
| TEFB | Trinity Executive Function Battery | 1,512 | 50-70% | [playra/trinity-tefb-cleaned](https://www.kaggle.com/datasets/playra/trinity-tefb-cleaned) |
| TSCP | Trinity Social Cognition Protocol | 25 | 60-80% | [playra/trinity-tscp-cleaned](https://www.kaggle.com/datasets/playra/trinity-tscp-cleaned) |

## Usage

### Single Track

```python
import kaggle_benchmarks as kbench
from trinity_benchmark import thlp_benchmark

# Run THLP benchmark
run = thlp_benchmark.run(kbench.llm)
```

### All Tracks

```python
import kaggle_benchmarks as kbench
from trinity_benchmark import trinity_all_tracks_benchmark

# Run all 5 benchmarks
run = trinity_all_tracks_benchmark.run(kbench.llm)
```

## Adversarial Features

Each track includes adversarial features designed to test true cognitive abilities:

### THLP (Pattern Learning)
- Pattern-breaking questions
- Negative constraints
- Paraphrased versions
- Complex reasoning

### TTM (Metacognition)
- Physics domain questions
- Counter-intuitive problems
- Multi-step reasoning
- Confidence calibration tests

### TAGP (Attention Control)
- Grid pattern breaking
- Memory interference
- Selective attention tests
- Sustained focus challenges

### TEFB (Executive Functions)
- Planning tasks
- Working memory tests
- Cognitive flexibility challenges
- Multi-step reasoning

### TSCP (Social Cognition)
- Theory of mind tasks
- Pragmatic inference
- Social reasoning
- Context understanding

## Key Findings

### TTM Dataset Issue

The original TTM dataset had **artificial structure**:
- 816 rows = 33 unique questions × 4 variants
- Each question appeared 4 times with different correct answers
- This gave 100% accuracy for pattern-matching models

**Solution:** Created physics-enhanced adversarial dataset (199 questions) with realistic structure.

## Citation

```bibtex
@online{Trinity Probes 2026},
  title={{Adversarial Benchmarks for Trinity Cognitive Probes}},
  author={{Vasilev, Dmitrii}},
  booktitle={{Kaggle Benchmarks}},
  year={{2026}},
  publisher={{Google DeepMind}},
  url={{https://github.com/gHashTag/agi-hackathon}}
}
```
