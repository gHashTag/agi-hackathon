#!/bin/bash

# Download Trinity Cognitive Probes datasets from Kaggle

set -e

TRACKS=(
    "https://www.kaggle.com/datasets/playra/hlp-mc"
    "https://www.kaggle.com/datasets/playra/tm-mc"
    "https://www.kaggle.com/datasets/playra/agp-mc"
    "https://www.kaggle.com/datasets/playra/efb-mc"
    "https://www.kaggle.com/datasets/playra/scp-mc"
)

TRACK_NAMES=("thlp" "ttm" "tagp" "tefb" "tscp")

echo "Downloading Trinity Cognitive Probes datasets..."

for i in "${!TRACKS[@]}"; do
    TRACK="${TRACK_NAMES[$i]}"
    echo "Downloading $TRACK..."

    # Navigate to track page
    ~/.browseros/bin/browseros-cli nav "${TRACKS[$i]}"
    sleep 2

    # Try to find and click download link
    # This will need manual interaction with the browser
done

echo ""
echo "Data structure:"
echo "data/"
echo "├── thlp/   # Pattern learning (19,681 questions)"
echo "├── ttm/     # Metacognitive calibration (733 questions)"
echo "├── tagp/    # Attention tasks (17,601 questions)"
echo "├── tefb/    # Executive functions (21,081 questions)"
echo "└── tscp/    # Social cognition (1,584 questions)"
