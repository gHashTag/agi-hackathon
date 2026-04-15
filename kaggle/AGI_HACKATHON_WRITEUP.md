# AGI Hackathon 2026 Writeup

## Team Information

- **Team Name**: [Your Team Name]
- **Members**: [List members]
- **GitHub**: https://github.com/gHashTag/agi-hackathon

## Hackathon Overview

The Google DeepMind x Kaggle "Measuring Progress Toward AGI" hackathon focuses on evaluating LLMs using the Trinity Cognitive Probes framework. The framework measures 5 key cognitive capabilities that are thought to be essential for AGI:

1. **THLP** - Pattern Learning: Inducing rules from examples
2. **TTM** - Metacognitive Calibration: Knowing what you know
3. **TAGP** - Attention Control: Selective and sustained focus
4. **TEFB** - Executive Functions: Multi-step planning and cognitive flexibility
5. **TSCP** - Social Cognition: Theory of Mind and pragmatic inference

## Our Approach

### Data Processing

We identified and fixed several issues in the original Kaggle datasets:

1. **THLP**: Multiline text in choice columns - flattened to single lines
2. **TTM**: UTF-8 encoding issues - re-encoded with proper handling
3. **TAGP**: Special characters - normalized to ASCII
4. **TEFB**: Answer formatting - standardized to single-letter answers
5. **TSCP**: CSV delimiter inconsistencies - standardized

Fixed datasets are available in `kaggle/data/`:
- thlp_mc_fixed.csv (19,680 questions)
- ttm_mc_fixed.csv (2,482 questions)
- tagp_mc_fixed.csv (17,600 questions)
- tefb_mc_fixed.csv (21,080 questions)
- tscp_mc_fixed.csv (2,839 questions)

**Total: 65,133 questions**

### Evaluation Framework

We built a modular evaluation framework (see: https://github.com/gHashTag/agi-hackathon-eval) supporting:

- **Claude 3.5 Sonnet** (Anthropic API)
- **GPT-4o** (OpenAI API)
- **Gemini 1.5 Flash** (Google API)
- **GLM-5** (Zhipu AI, experimental)

The framework includes:
- Unified prompt engineering with track-specific instructions
- Confidence tracking for calibration metrics
- Response time measurement
- Per-track and per-question-type analysis
- JSON output for easy result comparison

### Methodology

For each model and track:

1. **System Prompt**: Base AI assistant instructions + track-specific guidance
2. **Format**: Multiple choice with A/B/C/D options
3. **Metrics**:
   - Correctness: accuracy (60% weight)
   - Calibration: confidence alignment (20% weight)
   - Quality: reasoning depth (20% weight)

## Results

[Fill in actual results after running evaluations]

### Overall Performance

| Model | THLP | TTM | TAGP | TEFB | TSCP | Average |
|--------|------|-----|------|------|------|---------|
| Claude 3.5 | | | | | | |
| GPT-4o | | | | | | |
| Gemini 1.5 | | | | | | |

### Findings

[Describe key findings from your benchmark runs]

1. **Pattern Learning (THLP)**: [Observations]
2. **Metacognition (TTM)**: [Observations]
3. **Attention (TAGP)**: [Observations]
4. **Executive Functions (TEFB)**: [Observations]
5. **Social Cognition (TSCP)**: [Observations]

### Failure Analysis

Common failure modes identified:

- [Describe patterns in wrong answers]
- [Which cognitive capabilities are weakest?]
- [Are there systematic biases?]

## Conclusions

[Summarize what was learned about AGI progress]

- What did models perform best on?
- Where do current LLMs fall short?
- What would be needed to reach human-level performance?

## Future Work

- Fine-tune models on Trinity Cognitive Probes
- Explore ensemble approaches across cognitive tracks
- Investigate chain-of-thought vs direct answering
- Benchmark reasoning vs memorization

## References

- Trinity Cognitive Probes: [Link to paper]
- Google DeepMind Framework: [Link to hackathon page]
- Kaggle Datasets: [Link to datasets]

## License

This work is licensed under MIT License.
