#!/usr/bin/env python3
"""
Upload Kaggle Datasets Script
Prepares datasets for upload to Kaggle using Kaggle API
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

# Kaggle API configuration
KAGGLE_DATASETS = {
    "thlp": {
        "title": "Trinity Cognitive Probes - THLP Multiple Choice",
        "description": "THLP (Trinity Hierarchical Learning Pattern) cognitive track with 19,680 multiple choice questions. Focuses on pattern learning, inductive reasoning, and rule induction.",
        "file": "thlp_mc_fixed.csv"
    },
    "ttm": {
        "title": "Trinity Cognitive Probes - TTM Multiple Choice",
        "description": "TTM (Trinity Metacognitive) cognitive track with 2,482 multiple choice questions. Focuses on confidence calibration, error detection, and meta-learning.",
        "file": "ttm_mc_fixed.csv"
    },
    "tagp": {
        "title": "Trinity Cognitive Probes - TAGP Multiple Choice",
        "description": "TAGP (Trinity Attention Grid Pattern) cognitive track with 17,600 multiple choice questions. Focuses on selective attention, sustained focus, and attention shifting.",
        "file": "tagp_mc_fixed.csv"
    },
    "tefb": {
        "title": "Trinity Cognitive Probes - TEFB Multiple Choice",
        "description": "TEFB (Trinity Executive Function Battery) cognitive track with 21,080 multiple choice questions. Focuses on multi-step planning, working memory, and cognitive flexibility.",
        "file": "tefb_mc_fixed.csv"
    },
    "tscp": {
        "title": "Trinity Cognitive Probes - TSCP Multiple Choice",
        "description": "TSCP (Trinity Social Cognition Protocol) cognitive track with 2,839 multiple choice questions. Focuses on Theory of Mind, pragmatic inference, and social norms.",
        "file": "tscp_mc_fixed.csv"
    }
}

DATA_DIR = Path(__file__).parent.parent / "kaggle" / "data"


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


def upload_dataset(track: str):
    """Upload a single dataset to Kaggle"""
    if not HAS_KAGGLE:
        print(f"Cannot upload {track}: Kaggle API not available")
        return False

    if track not in KAGGLE_DATASETS:
        print(f"Error: Unknown track '{track}'")
        return False

    dataset_info = KAGGLE_DATASETS[track]
    file_path = DATA_DIR / dataset_info["file"]

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return False

    print(f"\n{'='*60}")
    print(f"Uploading {track.upper()} dataset")
    print(f"{'='*60}")
    print(f"Title: {dataset_info['title']}")
    print(f"File: {file_path}")

    try:
        api = KaggleApi()

        # Check if dataset exists
        print(f"\nChecking if dataset already exists...")

        # Create new dataset
        print(f"Creating new dataset...")
        api.dataset_create_new(
            folder=str(file_path.parent),
            title=dataset_info['title'],
            description=dataset_info['description']
        )

        print(f"✅ {track.upper()} uploaded successfully!")
        print(f"View at: https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-{track}-mc")

        return True

    except Exception as e:
        print(f"❌ Error uploading {track}: {e}")
        return False


def upload_all():
    """Upload all datasets"""
    print("="*60)
    print("Kaggle Dataset Upload Utility")
    print("="*60)

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


def main():
    """Main function"""
    if not HAS_KAGGLE:
        print("This script requires the Kaggle Python API")
        print("\nInstall: pip install kaggle")
        print("Authenticate: kaggle API")
        return

    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 upload_mc_datasets.py --track <thlp|ttm|tagp|tefb|tscp|all>")
        print("\nExamples:")
        print("  python3 upload_mc_datasets.py --track thlp")
        print("  python3 upload_mc_datasets.py --track all")
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
