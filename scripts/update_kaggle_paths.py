#!/usr/bin/env python3
import re

notebooks_dir = 'notebooks'

kaggle_paths = {
    'thlp': '/kaggle/input/trinity-cognitive-probes-thlp-mc/thlp_mc.csv',
    'ttm': '/kaggle/input/trinity-cognitive-probes-tmp-mc/ttm_mc.csv',
    'tagp': '/kaggle/input/trinity-cognitive-probes-tagp-mc/tagp_mc.csv',
    'tefb': '/kaggle/input/trinity-cognitive-probes-tefb-mc/tefb_mc.csv',
    'tscp': '/kaggle/input/trinity-cognitive-probes-tscp-mc/tscp_mc.csv'
}

notebook_tracks = {
    'thlp_mc_benchmark.ipynb': 'thlp',
    'tagp_mc_benchmark.ipynb': 'tagp',
    'tefb_mc_benchmark.ipynb': 'tefb',
    'tscp_mc_benchmark.ipynb': 'tscp',
    'ttm_mc_benchmark.ipynb': 'ttm'
}

print("📝 Updating Kaggle paths in notebooks...")

for nb_name, track in notebook_tracks.items():
    nb_path = f"{notebooks_dir}/{nb_name}"

    try:
        with open(nb_path, 'r', encoding='utf-8') as f:
            content = f.read()

        old_path = f"'/kaggle/input/trinity-cognitive-probes-{track}-mc/{track}_mc.csv'"

        # More flexible pattern matching
        patterns = [
            (old_path, f"CSV_PATH = '{kaggle_paths[track]}'"),
            (f"CSV_PATH = '/kaggle/input/trinity-cognitive-probes-{track}-mc/{track}_mc.csv'",
                f"CSV_PATH = '{kaggle_paths[track]}'"),
            (f"CSV_PATH = '/kaggle/input/trinity-cognitive-probes-{track}/{track}_mc/{track}_mc.csv'",
                f"CSV_PATH = '{kaggle_paths[track]}'"),
        ]

        updated = False
        for pattern, replacement in patterns:
            if pattern in content:
                new_content = content.replace(pattern, replacement)
                if new_content != content:
                    with open(nb_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    updated = True
                    print(f"✅ {nb_name}: {track} -> {kaggle_paths[track]}")
                break

        if not updated:
            # Try to find any CSV_PATH reference
            if 'CSV_PATH' in content:
                print(f"⚠️  {nb_name}: Found CSV_PATH but couldn't update")
            else:
                print(f"ℹ️  {nb_name}: No CSV_PATH found")

    except FileNotFoundError:
        print(f"⚠️  {nb_name} not found")
    except Exception as e:
        print(f"❌ {nb_name}: {e}")

print("\n✅ Update complete!")
