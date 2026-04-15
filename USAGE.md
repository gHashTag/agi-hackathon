# Quick Start Guide

## Test Single Question
```bash
cd agi-hackathon
python3 scripts/test_single.py --track thlp
```

## Evaluate All Tracks (Requires API Keys)
```bash
cd agi-hackathon

# Install dependencies
pip install -r requirements.txt

# Run evaluation
python3 scripts/evaluate.py --model claude --track all
```

## Download Kaggle Data
```bash
cd agi-hackathon
bash scripts/download_data.sh
```

## Fix Kaggle Datasets
```bash
cd agi-hackathon

# Fix multiline choices in TTM and TSCP
python3 scripts/fix_kaggle_datasets.py

# Then manually update About descriptions on Kaggle
# Visit: https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-<track>/edit
```

## Project Status

✅ Repository structure created
✅ Test scripts implemented
✅ Kaggle fix scripts created
✅ Evaluation prompts documented

## Known Issues
See README.md for details on Kaggle dataset issues
