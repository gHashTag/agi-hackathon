#!/usr/bin/env python3
"""Update all notebooks with adversarial datasets"""

import json
import csv
from pathlib import Path

# Notebooks to update
NOTEBOOKS = {
    "thlp_mc_benchmark.ipynb": "kaggle/data/extra/thlp_mc_adversarial.csv",
    "ttm_mc_benchmark.ipynb": "kaggle/data/extra/ttm_mc_physics_mc.csv",
    "tagp_mc_benchmark.ipynb": "kaggle/data/extra/tagp_mc_adversarial.csv",
    "tefb_mc_benchmark.ipynb": "kaggle/data/extra/tefb_mc_adversarial.csv",
    "tscp_mc_benchmark.ipynb": "kaggle/data/extra/tscp_mc_adversarial.csv"
}

def update_notebook(notebook_path, dataset_path):
    """Update single notebook"""
    if not notebook_path.exists():
        print(f"Skip {notebook_path.name}")
        return

    with open(notebook_path, 'r') as f:
        nb = json.load(f)

    updated = False
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'markdown':
            src = cell.get('source', '')

            if 'cognitive-probes-' in src and 'extra/' not in src:
                new_src = src.replace('cognitive-probes-', 'cognitive-probes-extra/')
                cell['source'] = new_src
                updated = True

    if updated:
        with open(notebook_path, 'w') as f:
            json.dump(nb, f, indent=2)
        print(f"Updated {notebook_path.name}")

def main():
    """Main function"""
    for nb_name, ds_path in NOTEBOOKS.items():
        nb_path = Path('notebooks') / nb_name
        ds_path = Path(ds_path)

        if ds_path.exists():
            print(f"Process {nb_name}: {ds_path}")
            update_notebook(nb_path, ds_path)
        else:
            print(f"Skip {nb_name}: {ds_path} not found")

    # Create submission template
    sub_path = Path('kaggle') / 'submission_template.csv'
    with open(sub_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'thlp_mc', 'ttm_mc', 'tagp_mc', 'tefb_mc', 'tscp_mc'])
        writer.writerow(['sample_1', 'A', 'B', 'C', 'D', 'A'])

    print(f"Created {sub_path}")

if __name__ == '__main__':
    main()