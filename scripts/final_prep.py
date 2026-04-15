#!/usr/bin/env python3
"""
Final preparation: Update notebook paths and create submission template
"""

import json
from pathlib import Path

# Map notebooks to their best datasets
NOTEBOOK_DATASETS = {
    'notebooks/thlp_mc_benchmark.ipynb': 'kaggle/data/extra/thlp_mc_aggressive.csv',
    'notebooks/ttm_mc_benchmark.ipynb': 'kaggle/data/extra/ttm_mc_adversarial_v3.csv',
    'notebooks/tagp_mc_benchmark.ipynb': 'kaggle/data/tagp_mc_aggressive.csv',
    'notebooks/tefb_mc_benchmark.ipynb': 'kaggle/data/extra/tefb_mc_cleaned.csv',
    'notebooks/tscp_mc_benchmark.ipynb': 'kaggle/data/extra/tscp_mc_cleaned.csv',
}

def update_notebook_csv_path(notebook_path, new_csv_path):
    """Update CSV path in notebook"""
    nb_path = Path(notebook_path)
    if not nb_path.exists():
        return False

    with open(nb_path) as f:
        nb = json.load(f)

    # Find cells with CSV references
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = ''.join(cell.get('source', []))

            # Replace common patterns
            old_patterns = [
                'thlp_mc_new.csv', 'thlp_mc_cleaned.csv',
                'ttm_mc_new.csv', 'ttm_mc_adversarial.csv',
                'tagp_mc.csv', 'tagp_mc_cleaned.csv',
                'tefb_mc_new.csv', 'tefb_mc_cleaned.csv',
                'tscp_mc_new.csv', 'tscp_mc_cleaned.csv',
            ]

            for old in old_patterns:
                if old in source:
                    source = source.replace(old, Path(new_csv_path).name)
                    cell['source'] = source.split('\n')
                    print(f"  ✓ Updated {old} -> {Path(new_csv_path).name}")
                    break

    # Save
    with open(nb_path, 'w') as f:
        json.dump(nb, f, indent=1)

    return True

def create_submission_template():
    """Create submission CSV template"""
    output = Path('kaggle/submission_template.csv')

    with open(output, 'w') as f:
        f.write('id,answer\n')
        f.write('sample_001,A\n')
        f.write('sample_002,B\n')
        f.write('sample_003,C\n')
        f.write('sample_004,D\n')

    print(f"\n✅ Created submission template: {output}")

def main():
    print("=" * 70)
    print("🔧 FINAL PREPARATION")
    print("=" * 70)

    print("\nUpdating notebooks...")
    updated = 0
    for nb_path, csv_path in NOTEBOOK_DATASETS.items():
        print(f"\n{Path(nb_path).name}:")
        print(f"  Target: {csv_path}")
        if update_notebook_csv_path(nb_path, csv_path):
            updated += 1

    create_submission_template()

    print("\n" + "=" * 70)
    print(f"✅ Updated {updated}/{len(NOTEBOOK_DATASETS)} notebooks")
    print("=" * 70)
    print("\n📋 NEXT STEPS:")
    print("1. Review notebooks in Jupyter")
    print("2. Run to verify they work")
    print("3. Create submission from results")
    print("4. Upload to Kaggle")
    print("=" * 70)

if __name__ == "__main__":
    main()
