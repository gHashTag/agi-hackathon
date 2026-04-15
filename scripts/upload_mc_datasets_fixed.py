#!/usr/bin/env python3
"""
Upload Fixed Kaggle Datasets Script
Uploads the _fixed.csv versions of datasets to Kaggle
"""

import os
from pathlib import Path

# Try to import Kaggle API
try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    HAS_KAGGLE = True
except ImportError:
    HAS_KAGGLE = False
    print("Error: kaggle package not installed")
    print("Install with: pip install kaggle")
    print("Authenticate with: kaggle API")

# Kaggle API configuration for fixed datasets
KAGGLE_DATASETS = {
    "thlp": {
        "title": "Trinity Cognitive Probes - THLP Multiple Choice (Fixed)",
        "description": "THLP (Trinity Hierarchical Learning Pattern) cognitive track with 19,680 multiple choice questions. **FIXED VERSION** - Multiline choices flattened, UTF-8 normalized. Focuses on pattern learning, inductive reasoning, and rule induction.\n\nSee fix report: https://github.com/gHashTag/agi-hackathon/blob/main/kaggle/KAGGLE_FIXES_REPORT.md",
        "file": "thlp_mc_fixed.csv",
        "slug": "trinity-cognitive-probes-thlp-mc"
    },
    "ttm": {
        "title": "Trinity Cognitive Probes - TTM Multiple Choice (Fixed)",
        "description": "TTM (Trinity Metacognitive) cognitive track with 2,482 multiple choice questions. **FIXED VERSION** - Encoding issues resolved, special characters normalized. Focuses on confidence calibration, error detection, and meta-learning.\n\nSee fix report: https://github.com/gHashTag/agi-hackathon/blob/main/kaggle/KAGGLE_FIXES_REPORT.md",
        "file": "ttm_mc_fixed.csv",
        "slug": "trinity-cognitive-probes-ttm-mc"
    },
    "tagp": {
        "title": "Trinity Cognitive Probes - TAGP Multiple Choice (Fixed)",
        "description": "TAGP (Trinity Attention Grid Pattern) cognitive track with 17,600 multiple choice questions. **FIXED VERSION** - Special characters normalized, markdown escaped. Focuses on selective attention, sustained focus, and attention shifting.\n\nSee fix report: https://github.com/gHashTag/agi-hackathon/blob/main/kaggle/KAGGLE_FIXES_REPORT.md",
        "file": "tagp_mc_fixed.csv",
        "slug": "trinity-cognitive-probes-tagp-mc"
    },
    "tefb": {
        "title": "Trinity Cognitive Probes - TEFB Multiple Choice (Fixed)",
        "description": "TEFB (Trinity Executive Function Battery) cognitive track with 21,080 multiple choice questions. **FIXED VERSION** - Answer format standardized to A/B/C/D. Focuses on multi-step planning, working memory, and cognitive flexibility.\n\nSee fix report: https://github.com/gHashTag/agi-hackathon/blob/main/kaggle/KAGGLE_FIXES_REPORT.md",
        "file": "tefb_mc_fixed.csv",
        "slug": "trinity-cognitive-probes-tefb-mc"
    },
    "tscp": {
        "title": "Trinity Cognitive Probes - TSCP Multiple Choice (Fixed)",
        "description": "TSCP (Trinity Social Cognition Protocol) cognitive track with 2,839 multiple choice questions. **FIXED VERSION** - CSV delimiters standardized, structure validated. Focuses on Theory of Mind, pragmatic inference, and social norms.\n\nSee fix report: https://github.com/gHashTag/agi-hackathon/blob/main/kaggle/KAGGLE_FIXES_REPORT.md",
        "file": "tscp_mc_fixed.csv",
        "slug": "trinity-cognitive-probes-tscp-mc"
    }
}

DATA_DIR = Path(__file__).parent.parent / "kaggle" / "data"
GITHUB_REPO = "https://github.com/gHashTag/agi-hackathon"
EVAL_REPO = "https://github.com/gHashTag/agi-hackathon-eval"


def check_api_credentials():
    """Check if Kaggle API credentials are configured"""
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"

    if not kaggle_json.exists():
        print("Error: Kaggle credentials not found")
        print("\nSetup:")
        print("1. Create Kaggle account: https://www.kaggle.com")
        print("2. Go to: https://www.kaggle.com/settings")
        print("3. Create API token")
        print("4. Run: kaggle API")
        print("\nToken will be saved to ~/.kaggle/kaggle.json")
        return False

    return True


def create_dataset_folder(track: str) -> Path:
    """Create a temporary folder structure for upload"""
    dataset_info = KAGGLE_DATASETS[track]
    file_path = DATA_DIR / dataset_info["file"]

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return None

    # Create folder named after the dataset
    upload_folder = Path(__file__).parent / "upload_temp" / track
    upload_folder.mkdir(parents=True, exist_ok=True)

    # Copy the fixed CSV to the folder
    import shutil
    shutil.copy(file_path, upload_folder / dataset_info["file"])

    # Create dataset-metadata.json
    metadata = {
        "title": dataset_info["title"],
        "description": dataset_info["description"],
        "licenses": [{"name": "MIT"}],
        "defaultFile": dataset_info["file"]
    }

    import json
    with open(upload_folder / "dataset-metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Created upload folder: {upload_folder}")
    return upload_folder


def upload_dataset(track: str):
    """Upload a single dataset to Kaggle"""
    if not HAS_KAGGLE:
        print(f"Cannot upload {track}: Kaggle API not available")
        return False

    if track not in KAGGLE_DATASETS:
        print(f"Error: Unknown track '{track}'")
        return False

    dataset_info = KAGGLE_DATASETS[track]

    print(f"\n{'='*60}")
    print(f"Uploading {track.upper()} dataset (Fixed Version)")
    print(f"{'='*60}")
    print(f"Title: {dataset_info['title']}")
    print(f"Questions: {dataset_info['file']}")

    # Create upload folder
    upload_folder = create_dataset_folder(track)
    if not upload_folder:
        return False

    try:
        api = KaggleApi()

        print(f"\nUploading to Kaggle...")

        # Upload the folder
        result = api.dataset_create_new(
            folder=str(upload_folder),
            quiet=False
        )

        print(f"✅ {track.upper()} uploaded successfully!")
        print(f"View at: https://www.kaggle.com/datasets/playra/{dataset_info['slug']}")

        # Clean up temp folder
        import shutil
        shutil.rmtree(upload_folder.parent)

        return True

    except Exception as e:
        print(f"❌ Error uploading {track}: {e}")
        print("\nYou may need to update the existing dataset instead:")
        print(f"1. Go to: https://www.kaggle.com/datasets/playra/{dataset_info['slug']}")
        print(f"2. Upload file manually")
        print(f"3. Update description with fix report link")
        return False


def upload_all():
    """Upload all fixed datasets"""
    print("="*60)
    print("Kaggle Fixed Dataset Upload Utility")
    print("="*60)
    print(f"Repository: {GITHUB_REPO}")
    print(f"Evaluation: {EVAL_REPO}")
    print()

    if not check_api_credentials():
        return

    results = {}
    for track in KAGGLE_DATASETS.keys():
        results[track] = upload_dataset(track)

    # Summary
    print(f"\n{'='*60}")
    print("UPLOAD SUMMARY")
    print(f"{'='*60}")

    for track, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {track.upper()}: {'Uploaded' if success else 'Failed'}")

    print(f"\n{GITHUB_REPO}")
    print(f"Evaluation code: {EVAL_REPO}")


def main():
    """Main function"""
    if not HAS_KAGGLE:
        print("This script requires the Kaggle Python API")
        print("\nInstall: pip install kaggle")
        print("Authenticate: kaggle API")
        return

    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 upload_mc_datasets_fixed.py --track <thlp|ttm|tagp|tefb|tscp|all>")
        print("\nExamples:")
        print("  python3 upload_mc_datasets_fixed.py --track thlp")
        print("  python3 upload_mc_datasets_fixed.py --track all")
        sys.exit(1)

    track = None
    i = 0
    while i < len(sys.argv):
        if sys.argv[i] == "--track":
            track = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    if not track:
        print("Error: --track is required")
        sys.exit(1)

    if track == "all":
        upload_all()
    else:
        upload_dataset(track)


if __name__ == "__main__":
    main()
