# Implementation Plan: Trinity Cognitive Probes Evaluation

## Status Overview

✅ **Repository Structure:** Complete  
⚠️ **Data:** Only sample data (need full download)  
⚠️ **API Integration:** Structure ready (need implementation)  
⏳ **Kaggle Updates:** Pending  

---

## PHASE 1: Data Preparation (Priority: CRITICAL)

### Task 1.1: Download Full Datasets from Kaggle
**Status:** ⏳ READY TO START  
**Estimated Time:** 30 minutes  
**Dependencies:** Kaggle API credentials

```bash
# Install Kaggle API
pip install kaggle

# Download all 5 tracks
kaggle datasets download -d playra/trinity-cognitive-probes-thlp-mc -p data/thlp/
kaggle datasets download -d playra/trinity-cognitive-probes-ttm-mc -p data/ttm/
kaggle datasets download -d playra/trinity-cognitive-probes-tagp-mc -p data/tagp/
kaggle datasets download -d playra/trinity-cognitive-probes-tefb-mc -p data/tefb/
kaggle datasets download -d playra/trinity-cognitive-probes-tscp-mc -p data/tscp/

# Unzip all
for dir in data/*/; do
  unzip "${dir}*.zip" -d "$dir" 2>/dev/null || true
done
```

**Verification:**
- [ ] THLP: 19,681 rows in thlp_mc_new.csv
- [ ] TTM: 4,931 rows in ttm_mc_new.csv  
- [ ] TAGP: 17,601 rows in tagp_mc.csv
- [ ] TEFB: 21,081 rows in tefb_mc_new.csv
- [ ] TSCP: 2,839 rows in tscp_mc_new.csv
**Total: 65,133 MC questions**

---

## PHASE 2: API Integration (Priority: CRITICAL)

### Task 2.1: Implement Anthropic Claude API
**Status:** ⏳ TO DO  
**File:** `scripts/evaluate.py`  
**Lines:** 72-85

```python
def evaluate(self, questions: List[Question]) -> List[EvaluationResult]:
    """Evaluate questions using Claude API"""
    import anthropic
    import re
    
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    results = []
    for q in questions:
        # Format prompt
        prompt = self.format_prompt(q)
        
        # Call API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            temperature=0.0,  # Deterministic for evaluation
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        result = self.parse_response(response.content[0].text, q)
        results.append(result)
    
    self.results = results
    return results
```

### Task 2.2: Implement OpenAI GPT-4o API
**Status:** ⏳ TO DO  
**File:** `scripts/evaluate.py`  
**Lines:** 103-115

Similar implementation using `openai` client with:
- Model: `gpt-4o-mini-2024-07-18` (cost-effective)
- Temperature: 0.0
- Max tokens: 500

### Task 2.3: Implement Google Gemini API
**Status:** ⏳ TO DO  
**File:** `scripts/evaluate.py`  
**Lines:** 88-100

Similar implementation using `google.generativeai` with:
- Model: `gemini-1.5-flash-latest`
- Temperature: 0.0

### Task 2.4: Add Response Parsing Logic
**New Method:** `parse_response(text: str, question: Question) -> EvaluationResult`

```python
def parse_response(self, text: str, q: Question) -> EvaluationResult:
    """Parse model response to extract answer, confidence, reasoning"""
    import re
    
    # Extract answer (A, B, C, D)
    answer_match = re.search(r'Answer:\s*([A-D])', text, re.IGNORECASE)
    predicted = answer_match.group(1).upper() if answer_match else "A"
    
    # Extract confidence (0-100)
    conf_match = re.search(r'Confidence:\s*(\d+)', text)
    confidence = int(conf_match.group(1)) if conf_match else 50
    confidence = max(0, min(100, confidence))  # Clamp to 0-100
    
    # Extract reasoning
    reasoning_match = re.search(r'Reasoning:\s*(.+?)(?=

|$)', text, re.DOTALL)
    reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"
    
    return EvaluationResult(
        question_id=q.id,
        track=q.question_type.split('_')[0].lower(),
        predicted=predicted,
        correct=(predicted == q.answer),
        confidence=confidence,
        reasoning=reasoning
    )
```

---

## PHASE 3: Evaluation Run (Priority: HIGH)

### Task 3.1: Create Sample Evaluation
**Status:** ⏳ TO DO  
**Command:**
```bash
python scripts/evaluate.py --model claude --track thlp --sample 100
```

**Expected Output:**
```
============================================================
Running evaluations for: claude
Tracks: thlp
Sample size: 100
============================================================

Loaded 100 questions from data/thlp/
Processing: 100%|████████████████| 100/100 [02:30<00:00, 1.53s/it]

Results saved to runs/claude/claude_results.json

============================================================
Evaluation Summary: claude
============================================================
Total Questions: 100
Correct: 78
Accuracy: 78.00%

Per-Track Breakdown:
- pattern_completion: 85% (20/20)
- belief_update: 75% (15/20)
- rule_induction: 80% (16/20)
- error_correction: 72% (14/20)
```

### Task 3.2: Full Evaluation (All Models, All Tracks)
**Status:** ⏳ TO DO  
**Estimated Time:** 6-8 hours  
**Cost Estimate:** $50-100 USD

```bash
# Run full evaluation on all models
for model in claude openai gemini; do
  python scripts/evaluate.py --model $model --track all
done
```

**Expected Results Summary:**
| Model | THLP | TTM | TAGP | TEFB | TSCP | Overall |
|-------|------|-----|------|------|------|---------|
| Claude-3.5 | TBD | TBD | TBD | TBD | TBD | TBD |
| GPT-4o-mini | TBD | TBD | TBD | TBD | TBD | TBD |
| Gemini-Flash | TBD | TBD | TBD | TBD | TBD | TBD |

---

## PHASE 4: Kaggle Dataset Updates (Priority: HIGH)

### Task 4.1: Update About Descriptions
**Status:** ⏳ TO DO  
**Manual Task:** Requires Kaggle web UI access

**For each track, update "About Dataset":**

```markdown
## Trinity [Track Name] - MC Format

Part of the Trinity Cognitive Probes benchmark for measuring AGI progress.

### Description
[Track-specific description from track_prompts.md]

### Source
GitHub Repository: https://github.com/gHashTag/agi-hackathon
Source (T27): https://github.com/gHashTag/t27

### Statistics
- Questions: [ACTUAL_COUNT]
- Format: Multiple Choice (A, B, C, D)
- License: CC0-1.0

### Citation
```bibtex
@dataset{trinity_cognitive_probes_2025,
  title={Trinity Cognitive Probes: 5-Track Benchmark for Cognitive AI},
  author={gHashTag},
  year={2025},
  url={https://github.com/gHashTag/agi-hackathon}
}
```
```

**Tracks to Update:**
- [ ] THLP - Add full description
- [ ] TAGP - Add full description
- [ ] TTM - Fix question count (733 → 4,931)
- [ ] TEFB - Fix question count (1,805 → 21,081)
- [ ] TSCP - Fix question count and remove MIT mention

---

## PHASE 5: Results Analysis & Reporting (Priority: MEDIUM)

### Task 5.1: Calibration Analysis
**Status:** ⏳ TO DO  
**New File:** `scripts/analyze_calibration.py`

```python
"""
Analyze confidence calibration across models and tracks
"""

import json
import numpy as np
import matplotlib.pyplot as plt

def analyze_calibration(results_path: str):
    """
    Expected calibration: confidence should correlate with accuracy
    Perfect calibration: 70% confidence → 70% accuracy
    """
    with open(results_path) as f:
        results = json.load(f)
    
    # Bin by confidence levels
    bins = [(0, 30), (30, 50), (50, 70), (70, 90), (90, 100)]
    
    for low, high in bins:
        bin_results = [r for r in results if low <= r['confidence'] < high]
        if bin_results:
            accuracy = sum(r['correct'] for r in bin_results) / len(bin_results)
            avg_confidence = sum(r['confidence'] for r in bin_results) / len(bin_results)
            print(f"Confidence {low}-{high}%: {accuracy:.1%} accuracy (n={len(bin_results)})")
```

### Task 5.2: Generate Report
**Status:** ⏳ TO DO  
**New File:** `docs/evaluation_report.md`

Sections:
1. Executive Summary
2. Methodology
3. Results by Track
4. Calibration Analysis
5. Model Comparison
6. Limitations
7. Conclusions

---

## PHASE 6: Repository Promotion (Priority: MEDIUM)

### Task 6.1: Update GitHub Repository
**Status:** ⏳ TO DO

- [ ] Add CITATION.cff
- [ ] Update README with evaluation results
- [ ] Add badges (Kaggle downloads, license)
- [ ] Create releases/tags
- [ ] Add CONTRIBUTING.md

### Task 6.2: Create Promotional Content
**Status:** ⏳ TO DO

- [ ] Write Medium article: "Trinity Cognitive Probes: A New Benchmark for AGI"
- [ ] Twitter/X thread with key findings
- [ ] LinkedIn post for professional audience
- [ ] Reddit post on r/MachineLearning

---

## Resource Requirements

### API Costs (Estimated)
| Model | Questions | Cost per 1K | Total Cost |
|-------|-----------|-------------|------------|
| Claude-3.5 | 65,133 | $3.00 | ~$195 |
| GPT-4o-mini | 65,133 | $0.15 | ~$10 |
| Gemini-Flash | 65,133 | $0.075 | ~$5 |
| **TOTAL** | | | **~$210** |

**Recommendation:** Start with sample_of_100 per track per model (~$10 total), then scale to full evaluation.

### Time Estimate
| Phase | Tasks | Time |
|-------|-------|------|
| Phase 1 | Data download | 30 min |
| Phase 2 | API integration | 2 hours |
| Phase 3 | Sample evaluation | 1 hour |
| Phase 3 | Full evaluation | 6-8 hours |
| Phase 4 | Kaggle updates | 1 hour |
| Phase 5 | Analysis & reporting | 3 hours |
| Phase 6 | Promotion | 2 hours |
| **TOTAL** | | **~16-20 hours** |

---

## Next Steps

### Immediate (Next 2 hours)
1. ✅ Download full datasets from Kaggle
2. ✅ Implement Claude API integration
3. ✅ Run sample evaluation (100 questions, 1 track)

### Short-term (This week)
4. Implement OpenAI and Gemini APIs
5. Run full evaluation on all models
6. Update Kaggle descriptions

### Medium-term (Next 2 weeks)
7. Complete analysis and reporting
8. Submit to NeurIPS/ICML Datasets track
9. Launch promotional campaign

---

**Status Legend:**
- ✅ Complete
- ⏳ In Progress
- ⚠️ Blocked/Issue
- ⏸️ Postponed

**Last Updated:** 2025-01-21
