# 🎯 Kaggle Submission Guide - Trinity Cognitive Probes

## ✅ STATUS: READY FOR SUBMISSION

---

## 📁 CRITICAL FILES TO UPLOAD

### 1. Adversarial Datasets (Required)

```
kaggle/data/extra/thlp_mc_aggressive.csv  (274 Q)
kaggle/data/extra/ttm_mc_physics_mc.csv    (199 Q - Physics Enhanced)
kaggle/data/tagp_mc_aggressive.csv       (851 Q)
kaggle/data/extra/tefb_mc_cleaned.csv       (1,512 Q)
kaggle/data/extra/tscp_mc_cleaned.csv       (25 Q)
```

### 2. Kaggle Notebooks (To Run)

```
notebooks/thlp_mc_benchmark.ipynb  - Update to use: thlp_mc_aggressive.csv
notebooks/ttm_mc_benchmark.ipynb  - Update to use: ttm_mc_physics_mc.csv
notebooks/tagp_mc_benchmark.ipynb  - Update to use: tagp_mc_aggressive.csv
notebooks/tefb_mc_benchmark.ipynb  - Update to use: tefb_mc_cleaned.csv
notebooks/tscp_mc_benchmark.ipynb  - Update to use: tscp_mc_cleaned.csv
```

### 3. Submission Template

```
kaggle/submission_template.csv - Format for Kaggle
```

---

## 🚀 STEP-BY-STEP SUBMISSION

### Step 1: Upload Datasets to Kaggle

1. Go to [Kaggle Datasets](https://www.kaggle.com/datasets)
2. Create 5 new datasets:
   - `playra/trinity-thlp-adversarial`
   - `playra/trinity-ttm-physics-enhanced`
   - `playra/trinity-tagp-adversarial`
   - `playra/trinity-tefb-cleaned`
   - `playra/trinity-tscp-cleaned`
3. Upload corresponding CSV files to each dataset

### Step 2: Update Notebooks

For each notebook (5 total):

1. Open notebook in Kaggle
2. Find cell with dataset loading
3. Change dataset path from original to adversarial:
   ```python
   # Original:
   CSV_PATH = next((f for f in csv_files if 'thlp_mc' in f.lower()), None)

   # Adversarial:
   CSV_PATH = 'kaggle/data/extra/thlp_mc_aggressive.csv'
   ```
4. Save notebook

### Step 3: Run Evaluation

1. Run each notebook to generate predictions
2. Results will be saved as CSV files

### Step 4: Submit to Competition

1. Go to [AGI Hackathon Competition](https://www.kaggle.com/competitions)
2. Click "Submit Predictions"
3. Upload your submission CSV following template format

---

## 📊 EXPECTED LEADERBOARD PERFORMANCE

| Metric | Expected | Description |
|--------|-----------|-------------|
| THLP Accuracy | 25-40% | Adversarial - breaks pattern matching |
| TTM Accuracy | 10-25% | Physics enhanced - truly adversarial |
| TAGP Accuracy | 20-35% | Aggressive - breaks memory patterns |
| TEFB Accuracy | 50-70% | Cleaned - realistic |
| TSCP Accuracy | 60-80% | Cleaned - small dataset |
| **Overall Score** | 2000-2500 | Depends on leaderboard composition |

---

## ⚠️ COMMON ISSUES & SOLUTIONS

### Issue 1: Notebook JSON Error
**Problem:** `Expecting property name enclosed in double quotes`

**Solution:** Use Kaggle's web interface to edit notebooks - don't download/upload JSON files directly. Copy-paste cells instead.

### Issue 2: Dataset Path Not Found
**Problem:** Notebook can't find adversarial dataset

**Solution:**
1. Ensure dataset is uploaded to Kaggle first
2. Use correct relative path: `'kaggle/data/extra/dataset.csv'`

### Issue 3: Answer Format Mismatch
**Problem:** Model predictions don't match expected format (A, B, C, D)

**Solution:** Ensure model outputs single letter (A-D) without extra text/spaces.

---

## 🎯 SUCCESS CRITERIA

### Minimum for Submission
- ✅ All 5 tracks submitted
- ✅ Adversarial datasets used (not original)
- ✅ Valid submission format

### Ideal Submission
- ✅ All 5 tracks have 30-70% accuracy (realistic)
- ✅ Physics questions integrated into TTM
- ✅ Visualizations included in notebooks
- ✅ Clear documentation in README

---

## 📝 DOCUMENTATION TO INCLUDE

In your notebook's README section, add:

```markdown
## Dataset Version
Using: Adversarial (Aggressive) Dataset
File: kaggle/data/extra/thlp_mc_aggressive.csv
Description: 274 questions designed to break memorization and test true cognitive capabilities.

## Evaluation Metrics
- Accuracy (overall)
- Accuracy by difficulty level
- Calibration (Brier score)
- Per-class accuracy

## Expected Results
- Overall Accuracy: ~30-40%
- Easy Questions: ~60-70%
- Medium Questions: ~30-40%
- Hard Questions: ~10-20%
```

---

## 🚀 FINAL CHECKLIST

Before submitting, verify:

- [ ] All 5 adversarial datasets uploaded to Kaggle
- [ ] All 5 notebooks updated to use adversarial datasets
- [ ] Each notebook tested with at least 10 questions
- [ ] Predictions follow required format (single letter A-D)
- [ ] Submission CSV follows template format
- [ ] README updated with dataset version info

---

**Good luck with your submission! 🎯**
