#!/usr/bin/env python3
"""Update notebooks to use adversarial datasets"""

import json
import csv
from pathlib import Path

# Map notebooks to their adversarial datasets
NOTEBOOKS = {
    'thlp_mc_benchmark.ipynb': 'kaggle/data/extra/thlp_mc_aggressive.csv',
    'ttm_mc_benchmark.ipynb': 'kaggle/data/extra/ttm_physics_mc.csv',
    'tagp_mc_benchmark.ipynb': 'kaggle/data/tagp_mc_aggressive.csv',
    'tefb_mc_benchmark.ipynb': 'kaggle/data/extra/tefb_mc_cleaned.csv',
    'tscp_mc_benchmark.ipynb': 'kaggle/data/extra/tscp_mc_cleaned.csv'
}

def update_notebook(nb_name, ds_path):
    """Update notebook to use adversarial dataset"""
    nb_path = Path('notebooks') / nb_name

    if not nb_path.exists():
        print(f"Skip {nb_name}")
        return

    with open(nb_path, 'r') as f:
        nb = json.load(f)

    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'markdown':
            src = cell.get('source', '')
            if 'Dataset:' in src and 'cognitive-probes-' in src:
                new_src = src.replace('cognitive-probes-', '')
                cell['source'] = new_src

    with open(nb_path, 'w') as f:
        json.dump(nb, f, indent=2)

    print(f"Updated {nb_name}")

def create_submission():
    """Create submission template"""
    sub_path = Path('kaggle/submission_template.csv')

    with open(sub_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'thlp_mc', 'ttm_mc', 'tagp_mc', 'tefb_mc', 'tscp_mc'])
        writer.writerow(['sample_1', 'A', 'B', 'C', 'D', 'A'])

    print(f"Created {sub_path}")

def main():
    for nb_name, ds_path in NOTEBOOKS.items():
        update_notebook(nb_name, ds_path)

    create_submission()
    print("Done!")

if __name__ == '__main__':
    main()