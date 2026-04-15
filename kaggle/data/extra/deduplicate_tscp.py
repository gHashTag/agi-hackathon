#!/usr/bin/env python3
"""Deduplicate TSCP multiple choice questions by question text."""

import pandas as pd

# Load the CSV file
input_file = "/Users/playra/agi-hackathon/kaggle/data/extra/tscp_mc_new.csv"
output_file = "/Users/playra/agi-hackathon/kaggle/data/extra/tscp_mc_cleaned.csv"

df = pd.read_csv(input_file)

# Count original rows
original_count = len(df)
print(f"Original rows: {original_count}")

# Create a normalized version of question text for comparison (lowercase, stripped)
df['_normalized_question'] = df['question'].str.strip().str.lower()

# Keep only the first occurrence of each unique question
df_cleaned = df.drop_duplicates(subset=['_normalized_question'], keep='first')

# Remove the temporary column
df_cleaned = df_cleaned.drop(columns=['_normalized_question'])

# Save cleaned version
df_cleaned.to_csv(output_file, index=False)

# Count cleaned rows
cleaned_count = len(df_cleaned)
duplicates_removed = original_count - cleaned_count

print(f"Cleaned rows: {cleaned_count}")
print(f"Duplicates removed: {duplicates_removed}")
print(f"Saved to: {output_file}")
