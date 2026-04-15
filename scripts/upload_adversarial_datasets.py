#!/usr/bin/env python3
"""
Upload adversarial datasets to Kaggle.

This script uploads all 5 adversarial datasets to Kaggle:
- THLP Aggressive (274 questions)
- TTM Physics Enhanced (199 questions)
- TAGP Adversarial (851 questions)
- TEFB Cleaned (1,512 questions)
- TSCP Cleaned (25 questions)
"""

import os
import subprocess
import json
import shutil

# Dataset configurations
DATASETS = [
    {
        "name": "trinity-thlp-adversarial",
        "title": "Trinity Cognitive Probes - THLP Adversarial",
        "description": "THLP (Trinity Hierarchical Learning Pattern) Adversarial Dataset - 274 questions designed to break memorization and test true cognitive capabilities. Expected model accuracy: 25-40%.",
        "source_file": "kaggle/data/extra/thlp_mc_aggressive.csv",
        "target_dir": "kaggle_upload/thlp"
    },
    {
        "name": "trinity-ttm-physics-enhanced",
        "title": "Trinity Cognitive Probes - TTM Physics Enhanced",
        "description": "TTM (Trinity Metacognitive) Physics-Enhanced Adversarial Dataset - 199 physics questions designed to test metacognitive calibration. Expected model accuracy: 10-25%.",
        "source_file": "kaggle/data/extra/ttm_physics_mc.csv",
        "target_dir": "kaggle_upload/ttm"
    },
    {
        "name": "trinity-tagp-adversarial",
        "title": "Trinity Cognitive Probes - TAGP Adversarial",
        "description": "TAGP (Trinity Attention Grid Pattern) Adversarial Dataset - 851 questions designed to test attention control capabilities. Expected model accuracy: 20-35%.",
        "source_file": "kaggle/data/tagp_mc_aggressive.csv",
        "target_dir": "kaggle_upload/tagp"
    },
    {
        "name": "trinity-tefb-cleaned",
        "title": "Trinity Cognitive Probes - TEFB Cleaned",
        "description": "TEFB (Trinity Executive Function Battery) Cleaned Dataset - 1,512 questions for evaluating executive function capabilities. Expected model accuracy: 50-70%.",
        "source_file": "kaggle/data/extra/tefb_mc_cleaned.csv",
        "target_dir": "kaggle_upload/tefb"
    },
    {
        "name": "trinity-tscp-cleaned",
        "title": "Trinity Cognitive Probes - TSCP Cleaned",
        "description": "TSCP (Trinity Social Cognition Protocol) Cleaned Dataset - 25 questions for theory of mind and pragmatic inference. Expected model accuracy: 60-80%.",
        "source_file": "kaggle/data/extra/tscp_mc_cleaned.csv",
        "target_dir": "kaggle_upload/tscp"
    },
]


def prepare_dataset(dataset):
    """Prepare dataset directory for Kaggle upload."""
    source_file = dataset["source_file"]
    target_dir = dataset["target_dir"]

    # Check source file exists
    if not os.path.exists(source_file):
        print(f"Warning: {source_file} not found, skipping")
        return None, None

    # Clean and create target directory
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir, exist_ok=True)

    # Copy CSV file
    csv_filename = os.path.basename(source_file)
    shutil.copy2(source_file, os.path.join(target_dir, csv_filename))

    # Create dataset-metadata.json
    metadata = {
        "title": dataset["title"],
        "id": f"playra/{dataset['name']}",
        "licenses": [{"name": "MIT"}],
        "description": dataset["description"],
        "keywords": ["cognitive", "ai", "benchmark", "adversarial", "agi"]
    }

    with open(os.path.join(target_dir, "dataset-metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    # Create README
    readme_content = f"""{dataset["title"]}

{dataset["description"]}

---

## Files
- `{csv_filename}` - Main dataset

## Citation
```bibtex
@online{{AGI Hackathon 2026}},
  title={{Trinity Cognitive Probes - Adversarial Datasets}},
  author={{Vasilev, Dmitrii}},
  booktitle={{Kaggle: The World's AI Proving Ground}},
  year={{2026}},
  publisher={{Google DeepMind}},
  url={{https://github.com/gHashTag/agi-hackathon}}
}}
```

## License
MIT License
"""
    with open(os.path.join(target_dir, "README.md"), "w") as f:
        f.write(readme_content)

    return target_dir, csv_filename


def upload_to_kaggle(dataset):
    """Upload dataset to Kaggle."""
    print(f"\n{'='*60}")
    print(f"Preparing: {dataset['name']}")
    print(f"{'='*60}")

    target_dir, csv_filename = prepare_dataset(dataset)

    if target_dir is None:
        print(f"✗ Skipped (source file not found)")
        return False

    print(f"✓ Prepared {target_dir}")
    print(f"✓ CSV file: {csv_filename}")

    # Kaggle upload command
    cmd = [
        "kaggle", "datasets", "create",
        "-p", target_dir,
        "-u",  # Public
    ]

    print(f"\nUploading to Kaggle...")
    print(f"  Dataset: playra/{dataset['name']}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✓ Successfully uploaded!")
            return True
        else:
            # Try to update if already exists
            print(f"Note: {result.stderr}")
            print("Trying to update existing dataset...")
            cmd_update = [
                "kaggle", "datasets", "version",
                "-p", target_dir,
                "-m", "Updated adversarial dataset"
            ]
            result = subprocess.run(cmd_update, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Successfully updated!")
                return True
            else:
                print(f"✗ Update failed: {result.stderr}")
                return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Upload all adversarial datasets."""
    print("="*60)
    print("KAGGLE ADVERSARIAL DATASET UPLOADER")
    print("="*60)

    results = []
    for dataset in DATASETS:
        success = upload_to_kaggle(dataset)
        results.append((dataset["name"], success))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, success in results:
        status = "✓" if success else "✗"
        print(f"{status} playra/{name}")

    successful = sum(1 for _, s in results if s)
    total = len(results)
    print(f"\nTotal: {successful}/{total} datasets uploaded")


if __name__ == "__main__":
    main()
