#!/usr/bin/env python3
"""
Update all Kaggle notebooks to use cleaned datasets
"""

import json
from pathlib import Path

# Mapping of notebooks to their cleaned datasets
NOTEBOOK_UPDATES = {
    'notebooks/thlp_mc_benchmark.ipynb': 'kaggle/data/extra/thlp_mc_cleaned.csv',
    'notebooks/ttm_mc_benchmark.ipynb': 'kaggle/data/extra/ttm_mc_adversarial_v3.csv',  # Use adversarial for TTM
    'notebooks/tagp_mc_benchmark.ipynb': 'kaggle/data/tagp_mc_cleaned.csv',
    'notebooks/tefb_mc_benchmark.ipynb': 'kaggle/data/extra/tefb_mc_cleaned.csv',
    'notebooks/tscp_mc_benchmark.ipynb': 'kaggle/data/extra/tscp_mc_cleaned.csv',
}

def update_notebook(notebook_path: str, new_csv_path: str) -> bool:
    """Update notebook to use cleaned dataset"""
    nb_path = Path(notebook_path)

    if not nb_path.exists():
        print(f"  ⚠️  {notebook_path} not found")
        return False

    try:
        with open(nb_path) as f:
            notebook = json.load(f)

        # Find and replace CSV path in code cells
        updated = False
        for cell in notebook.get('cells', []):
            if cell.get('cell_type') == 'code':
                source = ''.join(cell.get('source', []))
                if 'csv' in source.lower():
                    # Replace old CSV path with new one
                    old_patterns = [
                        'thlp_mc_new.csv',
                        'ttm_mc_new.csv',
                        'tagp_mc.csv',
                        'tefb_mc_new.csv',
                        'tscp_mc_new.csv',
                    ]

                    for old in old_patterns:
                        if old in source:
                            new_source = source.replace(old, Path(new_csv_path).name)
                            cell['source'] = new_source.split('\n')
                            updated = True
                            print(f"  ✓ Updated {old} -> {Path(new_csv_path).name}")

        if updated:
            # Backup original
            backup_path = nb_path.with_suffix('.ipynb.backup')
            with open(backup_path, 'w') as f:
                json.dump(notebook, f)

            # Save updated
            with open(nb_path, 'w') as f:
                json.dump(notebook, f, indent=1)
            return True

    except Exception as e:
        print(f"  ❌ Error updating {notebook_path}: {e}")
        return False

    return False

def main():
    print("=" * 70)
    print("🔧 UPDATING KAGGLE NOTEBOOKS WITH CLEANED DATASETS")
    print("=" * 70)

    updated_count = 0

    for notebook, csv_path in NOTEBOOK_UPDATES.items():
        print(f"\n📓 {Path(notebook).name}:")
        print(f"   Using: {csv_path}")

        if update_notebook(notebook, csv_path):
            updated_count += 1

    print("\n" + "=" * 70)
    print(f"✅ Updated {updated_count}/{len(NOTEBOOK_UPDATES)} notebooks")
    print("=" * 70)

if __name__ == "__main__":
    main()
