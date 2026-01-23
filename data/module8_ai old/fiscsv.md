Perfect — this is the **right fix point**.

You don’t want to *manually edit* the feature CSV.
You want a **clean Python script** that:

1. **Cleans labels**
2. **Removes leakage**
3. **Adds correct features**
4. **Balances the dataset**
5. Outputs a **corrected CSV** ready for AI training

Below is a **single, safe, reproducible script**.

---

# ✅ WHAT THIS SCRIPT WILL DO (EXACTLY)

Input
👉 `features_labels.csv` (your current one)

Output
👉 `features_labels_v2.csv` (corrected, AI-ready)

### Corrections applied

| Issue           | Fix                                     |
| --------------- | --------------------------------------- |
| 3-class labels  | Convert to **binary** (Calm / Not Calm) |
| CI leakage      | **REMOVE CI** from features             |
| Weak features   | Add **Alpha/Beta ratio**                |
| Class imbalance | **Downsample dominant class**           |
| Noise rows      | Remove invalid / zero values            |

This directly fixes the **“always Calm” prediction problem**.

---

# 📁 FILE LOCATIONS (IMPORTANT)

Place this script in:

```
scripts/
```

Input file must be here:

```
data/module8_ai/features_labels.csv
```

Output will be written to:

```
data/module8_ai/features_labels_v2.csv
```

---

# 🧪 PYTHON SCRIPT — FEATURE CSV CORRECTION

👉 Save as
`scripts/fix_features_csv.py`

```python
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
```

---

# ✅ WHAT YOU MUST CHECK AFTER RUNNING

Run:

```bash
python fix_features_csv.py
```

Then open:

```
data/module8_ai/features_labels_v2.csv
```

You should see:

### Columns

```
Alpha, Beta, AlphaBetaRatio, Label
```

### Labels

```
Calm
Not Calm
```

### Counts

* Calm ≈ Not Calm
  (no huge imbalance)

If this is true → **AI will stop predicting only Calm**.

---

# 🧠 HOW TO EXPLAIN THIS IN VIVA (MEMORIZE)

> “The feature dataset was cleaned to remove label leakage, rebalance class distribution, and include physiologically meaningful features before training the machine learning model.”

That sentence protects you completely.

---

# 🔜 NEXT STEP (DO NOT SKIP ORDER)

Now do **exactly this**:

1. Run `fix_features_csv.py`
2. Train AI using `features_labels_v2.csv`
3. Confirm confusion matrix shows **both classes**

Then come back and say:

> **“features_labels_v2.csv ready — give updated Module-9 real-time code”**

Do **not** jump ahead before that.
