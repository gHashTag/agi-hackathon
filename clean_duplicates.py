#!/usr/bin/env python3
"""Remove duplicate questions from tagp_mc.csv"""

import pandas as pd

# Load the CSV file
input_file = "/Users/playra/agi-hackathon/kaggle/data/tagp_mc.csv"
output_file = "/Users/playra/agi-hackathon/kaggle/data/tagp_mc_cleaned.csv"

print(f"Loading {input_file}...")
df = pd.read_csv(input_file)
original_count = len(df)
print(f"Original rows: {original_count}")

# Use the 'question' column directly
question_col = 'question'
print(f"Using question column: {question_col}")

# Create normalized version for grouping (case-insensitive, stripped)
df['_normalized_question'] = df[question_col].str.strip().str.lower()

# Keep first occurrence of each unique question
df_cleaned = df.drop_duplicates(subset='_normalized_question', keep='first')
df_cleaned = df_cleaned.drop(columns=['_normalized_question'])

cleaned_count = len(df_cleaned)
duplicates_removed = original_count - cleaned_count

# Save cleaned version
df_cleaned.to_csv(output_file, index=False)
print(f"Saved cleaned version to: {output_file}")
print(f"Cleaned rows: {cleaned_count}")
print(f"Duplicates removed: {duplicates_removed}")
print(f"Reduction: {100 * duplicates_removed / original_count:.1f}%")
