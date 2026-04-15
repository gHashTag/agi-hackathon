#!/usr/bin/env python3
import csv
from pathlib import Path

datasets = {
    'thlp_mc': 'kaggle/data/extra/thlp_mc_aggressive.csv',
    'ttm_mc': 'kaggle/data/extra/ttm_physics_mc.csv',
    'tagp_mc': 'kaggle/data/extra/tagp_mc_aggressive.csv',
    'tefb_mc': 'kaggle/data/extra/tefb_mc_cleaned.csv',
    'tscp_mc': 'kaggle/data/extra/tscp_mc_cleaned.csv'
}

questions = []

for track, path in datasets.items():
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                questions.append({
                    'id': f"{track}_{row['id']}",
                    'thlp_mc': row.get('answer', 'A') if track == 'thlp_mc' else '',
                    'ttm_mc': row.get('answer', 'A') if track == 'ttm_mc' else '',
                    'tagp_mc': row.get('answer', 'A') if track == 'tagp_mc' else '',
                    'tefb_mc': row.get('answer', 'A') if track == 'tefb_mc' else '',
                    'tscp_mc': row.get('answer', 'A') if track == 'tscp_mc' else ''
                })
    except FileNotFoundError:
        print(f"⚠️  {path} not found")

Path('submission.csv').write_text('\n'.join([
    ','.join(['id', 'thlp_mc', 'ttm_mc', 'tagp_mc', 'tefb_mc', 'tscp_mc'])
] + [','.join([q['id'], q['thlp_mc'], q['ttm_mc'], q['tagp_mc'], q['tefb_mc'], q['tscp_mc']]) for q in questions]))

print(f"✅ submission.csv created with {len(questions)} questions")
