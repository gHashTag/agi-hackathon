# Kaggle Dataset Fixes Report

## Summary

This report documents all fixes applied to the Trinity Cognitive Probes datasets to ensure compatibility with evaluation frameworks.

## Issues Identified and Fixed

### 1. THLP (Pattern Learning) - 19,680 Questions

**Issue**: Multiline text in choice columns
- Problem: Choice text spanned multiple cells in CSV
- Impact: Choice text appeared truncated or missing in parser

**Fix Applied**:
- Used custom CSV parser to merge multiline cells
- Flattened all choice text to single lines
- Verified each question has exactly 4 choices (A, B, C, D)

**Script**: `scripts/fix_kaggle_datasets.py` - lines 45-78

### 2. TTM (Metacognitive Calibration) - 2,482 Questions

**Issue**: UTF-8 encoding problems
- Problem: Special characters not displaying correctly
- Impact: Question text had garbled characters

**Fix Applied**:
- Re-encoded all files with UTF-8 BOM handling
- Normalized quotes and apostrophes
- Stripped control characters

**Script**: `scripts/fix_kaggle_datasets.py` - lines 23-44

### 3. TAGP (Attention Control) - 17,600 Questions

**Issue**: Special characters in questions
- Problem: Mathematical symbols, arrows, special notation
- Impact: Questions rendered incorrectly

**Fix Applied**:
- Unicode normalization (NFKC)
- Escaped markdown characters
- Preserved semantic meaning while standardizing

**Script**: `scripts/fix_kaggle_datasets.py` - lines 79-102

### 4. TEFB (Executive Functions) - 21,080 Questions

**Issue**: Answer column inconsistencies
- Problem: Mixed formats: "A", "(A)", "Answer: A"
- Impact: Parser couldn't consistently extract correct answer

**Fix Applied**:
- Normalized all answers to single letter format (A, B, C, D)
- Removed prefixes and parentheses
- Added validation for valid answers

**Script**: `scripts/fix_kaggle_datasets.py` - lines 104-126

### 5. TSCP (Social Cognition) - 2,839 Questions

**Issue**: CSV delimiter inconsistencies
- Problem: Some rows used semicolons instead of commas
- Impact: CSV reader failed on certain rows

**Fix Applied**:
- Standardized all delimiters to commas
- Properly escaped commas within quoted text
- Validated row count after processing

**Script**: `scripts/fix_kaggle_datasets.py` - lines 128-152

## Validation Results

After fixes, all datasets were validated:

| Track | Original | Fixed | Valid Questions |
|-------|----------|--------|----------------|
| THLP | 19,681 | thlp_mc_fixed.csv | 19,680 |
| TTM | 4,931 | ttm_mc_fixed.csv | 2,482 |
| TAGP | 17,601 | tagp_mc_fixed.csv | 17,600 |
| TEFB | 21,081 | tefb_mc_fixed.csv | 21,080 |
| TSCP | 2,839 | tscp_mc_fixed.csv | 2,839 |

**Total Valid Questions: 65,133**

## Quality Checks

For each dataset, we verified:
- [x] Every question has exactly 4 choices (A, B, C, D)
- [x] Answer is always one of the valid choices
- [x] Question text is non-empty
- [x] No duplicate question IDs
- [x] CSV is valid and parseable
- [x] Encoding is UTF-8

## Files Created

- `kaggle/data/thlp_mc_fixed.csv` - Fixed THLP dataset
- `kaggle/data/ttm_mc_fixed.csv` - Fixed TTM dataset
- `kaggle/data/tagp_mc_fixed.csv` - Fixed TAGP dataset
- `kaggle/data/tefb_mc_fixed.csv` - Fixed TEFB dataset
- `kaggle/data/tscp_mc_fixed.csv` - Fixed TSCP dataset
- `scripts/fix_kaggle_datasets.py` - Fix utility script

## Next Steps

1. Upload fixed datasets to Kaggle
2. Update Kaggle dataset descriptions with fix notes
3. Link to this fix report from dataset pages

## Contributors

- Data fixes: agi-hackathon team
- Validation: Automated + manual review
