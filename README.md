# AGI Hackathon 2026

Google DeepMind x Kaggle "Measuring Progress Toward AGI: A Cognitive Framework" Hackathon 2026

## Overview

This repository contains documentation, datasets, and evaluation resources for the AGI Hackathon 2026. We focus on evaluating 5 cognitive tracks from the Trinity Cognitive Probes framework.

## 5 Cognitive Tracks

| Track | Full Name | Questions | Focus |
|-------|-----------|-----------|-------|
| **THLP** | Trinity Hierarchical Learning Pattern | 19,680 | Pattern learning, inductive reasoning |
| **TTM** | Trinity Metacognitive | 2,482 | Confidence calibration, error detection |
| **TAGP** | Trinity Attention Grid Pattern | 17,600 | Selective attention, sustained focus |
| **TEFB** | Trinity Executive Function Battery | 21,080 | Planning, working memory, cognitive flexibility |
| **TSCP** | Trinity Social Cognition Protocol | 2,839 | Theory of Mind, pragmatic inference |

**Total: 65,133 Multiple Choice Questions**

## Quick Start

```bash
# Clone repository
git clone https://github.com/gHashTag/agi-hackathon.git
cd agi-hackathon

# Explore datasets
ls kaggle/data/

# Read documentation
cat kaggle/STATUS.md
cat kaggle/AGI_HACKATHON_WRITEUP.md
```

## Datasets

All datasets are in `kaggle/data/`:
- `thlp_mc_fixed.csv` - 19,680 THLP questions
- `ttm_mc_fixed.csv` - 2,482 TTM questions
- `tagp_mc_fixed.csv` - 17,600 TAGP questions
- `tefb_mc_fixed.csv` - 21,080 TEFB questions
- `tscp_mc_fixed.csv` - 2,839 TSCP questions

Each CSV contains:
- `id` - Question ID
- `question_type` - Cognitive sub-type
- `question` - Question text
- `A`, `B`, `C`, `D` - Answer choices
- `answer` - Correct answer (A/B/C/D)

## Documentation

- `kaggle/STATUS.md` - Dataset status and quality
- `kaggle/BENCHMARK_MODELS.md` - Model benchmarking guide
- `kaggle/REAL_MODEL_BENCHMARKS.md` - Real model results
- `kaggle/AGI_HACKATHON_WRITEUP.md` - Hackathon writeup
- `kaggle/KAGGLE_FIXES_REPORT.md` - Dataset fixes applied
- `kaggle/READY_TO_COMPETE.md` - Competition checklist

## Kaggle Datasets

- [THLP-MC](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-thlp-mc)
- [TTM-MC](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-ttm-mc)
- [TAGP-MC](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tagp-mc)
- [TEFB-MC](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tefb-mc)
- [TSCP-MC](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tscp-mc)

## Citation

```bibtex
@online{AGI Hackathon 2026},
  title={Measuring Progress Toward AGI: A Cognitive Framework Benchmark},
  author={{Vasilev, Dmitrii} and {Zhuang, Jiaming}},
  booktitle={Kaggle: The World's AI Proving Ground},
  year={2026},
  publisher={Google DeepMind},
  url={https://github.com/gHashTag/agi-hackathon}
}
```

## License

MIT License
