#!/usr/bin/env python3
"""
Update all Kaggle notebooks with adversarial datasets
"""

import json
from pathlib import Path

# Notebooks to update with adversarial datasets
NOTEBOOK_DATASETS = {
    "thlp_mc_benchmark.ipynb": "kaggle/data/extra/thlp_mc_adversarial.csv",
    "ttm_mc_benchmark.ipynb": "kaggle/data/extra/ttm_mc_physics_mc.csv",
    "tagp_mc_benchmark.ipynb": "kaggle/data/extra/tagp_mc_adversarial.csv",
    "tefb_mc_benchmark.ipynb": "kaggle/data/extra/tefb_mc_adversarial.csv",
    "tscp_mc_benchmark.ipynb": "kaggle/data/extra/tscp_mc_adversarial.csv"
}

# Common visualization templates
VIZ_TEMPLATES = {
    "thlp": """
# THLP Performance Visualization
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('kaggle/data/extra/thlp_mc_adversarial.csv')

# Performance by difficulty
fig, ax = plt.subplots(figsize=(10, 6))
df['difficulty'].value_counts().plot(kind='bar')
ax.set_title('THLP Performance by Difficulty')
plt.savefig('thlp_difficulty.png')
""",
    "ttm": """
# TTM Performance Comparison
import pandas as pd
import matplotlib.pyplot as plt

original = pd.read_csv('kaggle/data/ttm_mc.csv')
adversarial = pd.read_csv('kaggle/data/extra/ttm_mc_physics_mc.csv')

fig, ax = plt.subplots(figsize=(10, 6))
labels = ['Original', 'Adversarial']
sizes = [len(original), len(adversarial)]
ax.bar(labels, sizes)
ax.set_title('TTM: Original vs Adversarial')
ax.set_ylabel('Number of Questions')
plt.savefig('ttm_comparison.png')
""",
    "tagp": """
# TAGP Performance by Domain
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('kaggle/data/extra/tagp_mc_adversarial.csv')
df['domain'].value_counts().plot(kind='bar')
plt.title('TAGP Performance by Domain')
plt.savefig('tagp_domain.png')
""",
    "tefb": """
# TEFB Performance by Domain
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('kaggle/data/extra/tefb_mc_adversarial.csv')
df['domain'].value_counts().plot(kind='bar')
plt.title('TEFB Performance by Domain')
plt.savefig('tefb_domain.png')
""",
    "tscp": """
# TSCP Performance by Difficulty
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('kaggle/data/extra/tscp_mc_adversarial.csv')
df['difficulty'].value_counts().plot(kind='bar')
plt.title('TSCP Performance by Difficulty')
plt.savefig('tscp_difficulty.png')
"""
}

def update_notebook(notebook_path, dataset_path, viz_template):
    """Update a single notebook with adversarial dataset and visualization"""

    if not notebook_path.exists():
        print(f"⚠  Notebook {notebook_path} not found!")
        return False

    # Read notebook
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)

    # Update dataset path
    updated = False
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'markdown':
            source = cell.get('source', '')

            # Update dataset path in markdown cells
            if 'Dataset:' in source and 'extra/' not in source:
                new_source = source.replace('cognitive-probes-', 'cognitive-probes-extra/')
                new_source = new_source.replace('cognitive-probes/', 'cognitive-probes/extra/')
                cell['source'] = new_source
                updated = True

            # Add visualization
            if '## Visualizations' not in source and viz_template:
                cell['source'] += f"\n\n## Visualizations\n\n{viz_template}"
                updated = True

    # Save updated notebook
    if updated:
        with open(notebook_path, 'w') as f:
            json.dump(notebook, f, indent=2)
        print(f"✅ Updated {notebook_path.name}")
        return True
    else:
        print(f"✅ {notebook_path.name} already up to date")
        return True

def create_submission_template():
    """Create Kaggle submission template"""
    template_path = Path('kaggle') / 'submission_template.csv'

    fieldnames = ['id', 'thlp_mc', 'ttm_mc', 'tagp_mc', 'tefb_mc', 'tscp_mc']

    with open(template_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)

        # Write sample submission row
        sample_row = ['sample_1', 'A', 'B', 'C', 'D', 'A']
        writer.writerow(sample_row)

    print(f"✅ Created submission template at {template_path}")

def main():
    """Main execution function"""
    # Update all notebooks
    success_count = 0

    for notebook_name, dataset_path in NOTEBOOK_DATASETS.items():
        notebook_path = Path('notebooks') / notebook_name

        # Get viz template based on track
        track = notebook_name.split('_')[0]  # thlp, ttm, tagp, tefb, tscp
        viz_template = VIZ_TEMPLATES.get(track, '')

        if update_notebook(notebook_path, dataset_path, viz_template):
            success_count += 1

    print(f"\n📊 Updated {success_count} out of {len(NOTEBOOK_DATASETS)} notebooks")

    # Create submission template
    create_submission_template()

    print(f"\n✅ All notebooks updated!")
    print(f"✅ Submission template created!")
    print(f"\n🚀 Ready for Kaggle submission!")

if __name__ == '__main__':
    main()