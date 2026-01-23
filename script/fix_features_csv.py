import pandas as pd
import numpy as np
import os

# ---------------- PATHS ----------------
DATA_PATH = "../data/module8_ai/"
INPUT_FILE = DATA_PATH + "features_labels.csv"
OUTPUT_FILE = DATA_PATH + "features_labels_v2.csv"
# --------------------------------------

# -------- LOAD CSV --------
df = pd.read_csv(INPUT_FILE)

print("\nOriginal label distribution:")
print(df["Label"].value_counts())

# -------- CLEAN LABELS --------
# Collapse to binary classes
df["Label"] = df["Label"].replace({
    "Neutral": "Not Calm",
    "Not Calm": "Not Calm",
    "Calm": "Calm"
})

# -------- REMOVE INVALID ROWS --------
df = df[(df["Alpha"] > 0) & (df["Beta"] > 0)]

# -------- REMOVE LEAKAGE FEATURE --------
if "CI" in df.columns:
    df = df.drop(columns=["CI"])

# -------- ADD ROBUST FEATURE --------
df["AlphaBetaRatio"] = df["Alpha"] / df["Beta"]

# -------- CHECK DISTRIBUTION --------
print("\nLabel distribution after cleaning:")
print(df["Label"].value_counts())

# -------- BALANCE DATASET --------
calm_df = df[df["Label"] == "Calm"]
not_calm_df = df[df["Label"] == "Not Calm"]

min_count = min(len(calm_df), len(not_calm_df))

calm_df = calm_df.sample(min_count, random_state=42)
not_calm_df = not_calm_df.sample(min_count, random_state=42)

balanced_df = pd.concat([calm_df, not_calm_df]).sample(frac=1, random_state=42)

print("\nBalanced label distribution:")
print(balanced_df["Label"].value_counts())

# -------- SAVE CLEAN CSV --------
balanced_df.to_csv(OUTPUT_FILE, index=False)

print("\nCorrected feature CSV saved as:")
print(OUTPUT_FILE)
