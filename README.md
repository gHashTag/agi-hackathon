# Measuring Progress Toward AGI - Cognitive Abilities

**Official implementation of** Google DeepMind x Kaggle "Measuring Progress Toward AGI: A Cognitive Framework" Hackathon 2026

---

## 🌐 Overview

This repository contains a complete evaluation framework for the AGI Hackathon, enabling systematic assessment of Large Language Models across five cognitive tracks defined by Google DeepMind's research.

### The 5 Cognitive Tracks

| Track | Cognitive Ability | Brain Zones | Questions | GitHub Dataset |
|-------|------------------|------------|------------|---------------|
| **THLP** | Pattern Learning | Hippocampus, Entorhinal Cortex | [THLP Dataset](https://www.kaggle.com/datasets/playra/hlp-mc) |
| **TTM** | Metacognitive Calibration | Prefrontal Cortex | [TTM Dataset](https://www.kaggle.com/datasets/playra/tm-mc) |
| **TAGP** | Selective Attention | Parietal Lobes | [TAGP Dataset](https://www.kaggle.com/datasets/playra/agp-mc) |
| **TEFB** | Executive Functions | DLPFC | [TEFB Dataset](https://www.kaggle.com/datasets/playra/efb-mc) |
| **TSCP** | Social Cognition | TPJ, mPFC | [TSCP Dataset](https://www.kaggle.com/datasets/playra/scp-mc) |

**Total Questions:** 65,133 multiple-choice questions spanning all cognitive tracks

---

## 🎯 Features

- ✅ **GitHub Repository:** https://github.com/gHashTag/agi-hackathon
- ✅ **Complete Evaluation Pipeline:** Support for Claude, GPT-4, Gemini, and other LLMs
- ✅ **Test Suite:** Single question testing for development and validation
- ✅ **Kaggle Integration:** Dataset fixes for Data Explorer compatibility
- ✅ **Prompt Engineering:** Track-specific system prompts for optimal performance
- ✅ **Results Analysis:** Automated scoring, calibration analysis, and comparison tools

---

## 🚀 Quick Start

### Prerequisites
```bash
# Clone the repository
git clone https://github.com/gHashTag/agi-hackathon.git
cd agi-hackathon

# Install dependencies
pip install -r requirements.txt
```

### Test Single Question
```bash
# Quick test with a sample question
python3 scripts/test_single.py --track thlp
```

### Full Evaluation
```bash
# Set your API keys (choose one or all)
export ANTHROPIC_API_KEY="your-claude-api-key"
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_API_KEY="your-gemini-api-key"

# Run evaluation on all tracks (sample mode for testing)
python3 scripts/evaluate.py --model claude --track all --sample 100

# Or evaluate on specific tracks
python3 scripts/evaluate.py --model gpt-4 --track ttm --sample 50
python3 scripts/evaluate.py --model gemini --track tagp
```

---

## 📁 Project Structure

```
agi-hackathon/
├── README.md                      # This file - complete overview
├── CITATION.cff                  # Citation metadata for academic papers
├── requirements.txt                 # Python dependencies
├── KAGGLE_UPDATE.md                # Guide for updating Kaggle datasets
├── IMPLEMENTATION_PLAN.md          # Development roadmap
│
├── data/                          # Downloaded Kaggle datasets
│   ├── thlp/                    # Pattern Learning (19,681 Q)
│   ├── ttm/                     # Metacognitive Calibration (4,931 Q)
│   ├── tagp/                    # Attention Tasks (17,601 Q)
│   ├── tefb/                    # Executive Functions (21,081 Q)
│   └── tscp/                    # Social Cognition (2,839 Q)
├── runs/                           # Evaluation results
│   ├── claude/                  # Claude evaluation results
│   ├── openai/                  # GPT-4 results
│   └── gemini/                  # Gemini results
├── prompts/                         # Evaluation prompts
│   ├── system_prompts.md         # Base system prompts
│   └── track_prompts.md           # Track-specific instructions
└── scripts/                          # Utility scripts
    ├── evaluate.py               # Main evaluation pipeline ⭐
    ├── test_single.py           # Single question tester
    ├── download_data.py           # Kaggle dataset downloader
    ├── fix_kaggle_datasets.py  # Dataset compatibility fixes
    └── analyze_results.py        # Results analysis tool
```

---

## 🎯 Supported Models

| Model | Provider | API Key | Cost per 1K Questions |
|--------|----------|----------------------|
| **Claude 3.5 Sonnet** | Anthropic | `ANTHROPIC_API_KEY` | ~$3.00 |
| **GPT-4o** | OpenAI | `OPENAI_API_KEY` | ~$0.15 |
| **Gemini 1.5 Flash** | Google | `GOOGLE_API_KEY` | ~$0.08 |

---

## 📊 Evaluation Methodology

### Question Format
Each question uses standardized multiple-choice format:
- **id**: Unique question identifier
- **question_type**: Cognitive track identifier
- **question**: Task description
- **choices**: Four options (A, B, C, D)
- **answer**: Correct answer (A-D)

### Scoring System
Based on Google DeepMind's specification:
- **Correctness (60%)**: Binary accuracy - does answer match ground truth?
- **Calibration (20%)**: How well do confidence scores correlate with actual accuracy?
- **Quality (20%)**: Does reasoning demonstrate true understanding?

**Composite Score:** = (Correctness × 0.6) + (Calibration × 0.2) + (Quality × 0.2)

### Output Format Required by Kaggle
For each question, models respond with:
```
Answer: [A|B|C|D]
Confidence: [0-100]
Reasoning: [Brief explanation 2-3 sentences]
```

### Response Parsing
Robust parsing handles:
- Multi-line reasoning extraction
- Confidence value validation (0-100 range)
- Answer validation (A, B, C, D only)

---

## 🔬 Citation

If you use this code or framework in academic work, please cite:

**BibTeX:**
```bibtex
@online{Measuring Progress Toward AGI Hackathon 2026},
  title={Measuring Progress Toward AGI: A Cognitive Framework Benchmark},
  author={{Vasilev, Dmitrii} and {Zhuang, Jiaming}},
  booktitle={Kaggle: The World's AI Proving Ground},
  year={2026},
  publisher={Google DeepMind},
  note={Official implementation repository for the AGI Hackathon evaluation framework},
  url={https://github.com/gHashTag/agi-hackathon}
}
```

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional model integrations (local models, other APIs)
- Enhanced prompting strategies
- Advanced analysis tools and visualizations
- Performance optimization and caching
- Documentation improvements

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

**🎯 Ready for the hackathon!**

- All 5 tracks loaded and ready for evaluation
- Evaluation pipeline supports multiple LLM providers
- Kaggle datasets prepped and documented
- Comprehensive prompt engineering for optimal model performance

For questions or issues, open an issue on [GitHub Issues](https://github.com/gHashTag/agi-hackathon/issues).
