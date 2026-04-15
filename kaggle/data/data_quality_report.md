================================================================================
DATA QUALITY VALIDATION REPORT
Trinity Cognitive Probes - Adversarial Datasets
================================================================================

## SUMMARY

| Dataset | Questions | Duplicates | Uniform | Adversarial | Quality |
|----------|-----------|------------|---------|------------|----------|----------|
| ttm_physics_mc       |        49 |        2 |        ✅ |        1 | ⚠️ Needs Work |
| tagp_mc_adversarial  |       125 |       37 |        ✅ |        4 |   ✅ Good |
| tefb_mc_cleaned      |      1512 |       64 |        ✅ |        1 | ⚠️ Needs Work |
| tscp_mc_cleaned      |        25 |        0 |        ✅ |        2 | ⚠️ Needs Work |

## DETAILED ANALYSIS

### Ttm Physics Mc

**Duplicates:**
- Exact: 0
- Answer Patterns: 2
- Semantic: 0

**Answer Distribution:**
- Total Questions: 49
- Valid Answers: 49
- Invalid Answers: 0
- C: 34.7%
- A: 32.7%
- B: 30.6%
- D: 2.0%
- KL Divergence: -0.063
- Uniform: ✅ Yes

**Adversarial Quality:**
- Adversarial Indicators: 1
  - paraphrasing: 2 instances

**Question Complexity:**
- Average Length: 173.9 chars
- Median Length: 179.0 chars
- Average Choices: 1.00
- Average Choice Length: 40.7 chars

------------------------------------------------------------
### Tagp Mc Adversarial

**Duplicates:**
- Exact: 0
- Answer Patterns: 37
- Semantic: 0

**Answer Distribution:**
- Total Questions: 125
- Valid Answers: 125
- Invalid Answers: 0
- D: 28.8%
- C: 28.8%
- A: 24.8%
- B: 17.6%
- KL Divergence: -0.066
- Uniform: ✅ Yes

**Adversarial Quality:**
- Adversarial Indicators: 4
  - negative_constraint: 347 instances
  - paraphrasing: 251 instances
  - trick_questions: 97 instances
  - complex_reasoning: 47 instances

**Question Complexity:**
- Average Length: 373.8 chars
- Median Length: 384.0 chars
- Average Choices: 1.00
- Average Choice Length: 100.1 chars

------------------------------------------------------------
### Tefb Mc Cleaned

**Duplicates:**
- Exact: 0
- Answer Patterns: 64
- Semantic: 0

**Answer Distribution:**
- Total Questions: 1512
- Valid Answers: 1512
- Invalid Answers: 0
- D: 26.5%
- A: 24.6%
- C: 24.5%
- B: 24.4%
- KL Divergence: -0.066
- Uniform: ✅ Yes

**Adversarial Quality:**
- Adversarial Indicators: 1
  - negative_constraint: 406 instances

**Question Complexity:**
- Average Length: 163.5 chars
- Median Length: 170.5 chars
- Average Choices: 1.00
- Average Choice Length: 109.5 chars

------------------------------------------------------------
### Tscp Mc Cleaned

**Duplicates:**
- Exact: 0
- Answer Patterns: 0
- Semantic: 0

**Answer Distribution:**
- Total Questions: 25
- Valid Answers: 25
- Invalid Answers: 0
- D: 32.0%
- A: 32.0%
- C: 20.0%
- B: 16.0%
- KL Divergence: -0.066
- Uniform: ✅ Yes

**Adversarial Quality:**
- Adversarial Indicators: 2
  - negative_constraint: 5 instances
  - paraphrasing: 1 instances

**Question Complexity:**
- Average Length: 151.9 chars
- Median Length: 141.0 chars
- Average Choices: 1.00
- Average Choice Length: 224.6 chars

------------------------------------------------------------
## RECOMMENDATIONS

### General
- ✅ All datasets should have < 5% duplicates
- ✅ Answer distribution should be close to uniform (KL < 0.3)
- ✅ Adversarial indicators: 3+ for robust evaluation

### Per-Dataset
- **THLP**: Target 25-40% accuracy, needs strong adversarial
- **TTM**: Physics enhanced, target 10-25% accuracy
- **TAGP**: Abstract reasoning, target 20-35% accuracy
- **TEFB**: Executive function, target 50-70% accuracy
- **TSCP**: Small dataset (25 Q), target 60-80% accuracy