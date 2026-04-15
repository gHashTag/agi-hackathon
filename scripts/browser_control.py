#!/usr/bin/env python3
"""
BrowserOS Control Script for Kaggle Downloads
Automates dataset downloads from Kaggle using BrowserOS CLI
"""

import subprocess
import sys
from pathlib import Path

# Kaggle dataset URLs
TRACKS = {
    "thlp": "https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-thlp-mc",
    "ttm": "https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-ttm-mc",
    "tagp": "https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tagp-mc",
    "tefb": "https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tefb-mc",
    "tscp": "https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tscp-mc"
}

BROWSEROS_CLI = "~/.browseros/bin/browseros-cli"


def run_command(cmd: str) -> str:
    """Execute BrowserOS CLI command and return output"""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=120
    )
    return result.stdout


def navigate_to_dataset(track: str) -> bool:
    """Navigate to Kaggle dataset page"""
    url = TRACKS[track]
    print(f"Navigating to {url}")

    output = run_command(f"{BROWSEROS_CLI} nav {url}")
    sleep_cmd = run_command("sleep 3")

    return "Success" in output or "error" not in output.lower()


def find_download_button() -> str | None:
    """Find download button on page"""
    output = run_command(f"{BROWSEROS_CLI} snap")

    if "Download" in output:
        # Parse for download element reference
        for line in output.split('\n'):
            if "Download" in line and "clickable" in line:
                # Extract element reference
                parts = line.split(']')
                if len(parts) > 1:
                    return parts[0] + ']'

    return None
    else:
        return None


def click_download(button_ref: str) -> bool:
    """Click download button"""
    print(f"Clicking: {button_ref}")

    output = run_command(f"{BROWSEROS_CLI} click {button_ref}")
    sleep_cmd = run_command("sleep 5")

    return "error" not in output.lower()


def download_track(track: str) -> bool:
    """Download dataset for single track"""
    print(f"\n{'='*60}")
    print(f"Downloading {track.upper()} dataset")
    print(f"{'='*60}")

    if track not in TRACKS:
        print(f"Error: Unknown track '{track}'")
        print(f"Valid tracks: {', '.join(TRACKS.keys())}")
        return False

    # Navigate to dataset page
    if not navigate_to_dataset(track):
        print("Error: Could not navigate to dataset page")
        return False

    # Find download button
    button = find_download_button()
    if not button:
        print("Warning: Could not find download button")
        print("You may need to click manually in the browser")
        return False

    # Click download
    if not click_download(button):
        print("Error: Failed to click download button")
        return False

    print(f"\n✅ {track.upper()} download initiated")
    return True


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python3 browser_control.py --track <thlp|ttm|tagp|tefb|tscp|all>")
        print("\nExamples:")
        print("  python3 browser_control.py --track thlp")
        print("  python3 browser_control.py --track all")
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

    # Download requested tracks
    if track == "all":
        for t in TRACKS:
            download_track(t)
    else:
        download_track(track)


if __name__ == "__main__":
    main()
