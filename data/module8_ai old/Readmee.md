# ✅ SHORT ANSWER (BLUNT)

The AI input CSV is:

```
features_labels.csv
```

It is **NOT collected directly from Arduino**
It is **NOT raw EEG**
It is **DERIVED from files you already generated**

It is built from **these two outputs**:

1. `bandpower_windows.csv`  ← from **Module-6**
2. `calmness_timeline.csv`  ← from **Module-7 (deterministic logic)**

AI sits **on top of these**, not below them.

---

# 🧠 FULL DATA FLOW (UNDERSTAND THIS)

```
EEG → Filtering → FFT → Alpha/Beta
      ↓
bandpower_windows.csv
      ↓
Calmness Index + thresholds
      ↓
calmness_timeline.csv
      ↓
features_labels.csv  ← AI INPUT
```

If you understand this pipeline, you can answer **any viva question**.

---

# 📄 FILE 1: bandpower_windows.csv (SOURCE OF FEATURES)

You already created this in **Module-6**.

📍 Location:

```
data/module6_bandpower_extraction/bandpower_windows.csv
```

Format:

```csv
Window,Alpha_Power,Beta_Power
1,0.0000123,0.0000089
2,0.0000131,0.0000075
3,0.0000119,0.0000092
```

This gives you:

* Alpha power
* Beta power

These are **raw numerical features**.

---

# 📄 FILE 2: calmness_timeline.csv (SOURCE OF LABELS)

You created this in **Module-7**.

📍 Location:

```
data/module7_calmness_final/calmness_timeline.csv
```

Format:

```csv
Window,Alpha,Beta,Calmness_Index,State
1,0.0000123,0.0000089,1.38,Calm
2,0.0000131,0.0000075,1.75,Calm
3,0.0000119,0.0000092,1.29,Neutral
```

This gives you:

* Calmness Index
* **State label** (Calm / Neutral / Not Calm)

These labels come from **deterministic logic**, not humans.

---

# 🎯 WHAT AI NEEDS (FINAL ANSWER)

AI needs **one CSV** with:

| Column | From where            |
| ------ | --------------------- |
| Alpha  | bandpower_windows.csv |
| Beta   | bandpower_windows.csv |
| CI     | calmness_timeline.csv |
| Label  | calmness_timeline.csv |

That file is called:

```
features_labels.csv
```

---

# 🧪 HOW TO CREATE features_labels.csv (DO THIS)

## 📁 Save it here:

```
data/module8_ai/features_labels.csv
```

## 📄 Format (EXACT)

```csv
Alpha,Beta,CI,Label
0.0000123,0.0000089,1.38,Calm
0.0000131,0.0000075,1.75,Calm
0.0000119,0.0000092,1.29,Neutral
```

---

# 🧪 AUTOMATIC SCRIPT TO GENERATE IT (USE THIS)

👉 Save as
`scripts/make_features_labels.py`

```python
import csv
import os

BANDPOWER_FILE = "../data/module6_bandpower_extraction/bandpower_windows.csv"
CALMNESS_FILE  = "../data/module7_calmness_final/calmness_timeline.csv"
OUT_PATH = "../data/module8_ai/"
OUT_FILE = OUT_PATH + "features_labels.csv"

os.makedirs(OUT_PATH, exist_ok=True)

# Load bandpower
bandpower = {}
with open(BANDPOWER_FILE, "r") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        bandpower[int(row[0])] = {
            "alpha": float(row[1]),
            "beta": float(row[2])
        }

# Load calmness + labels
rows = []
with open(CALMNESS_FILE, "r") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        window = int(row[0])
        ci = float(row[3])
        label = row[4]

        if window in bandpower:
            rows.append([
                bandpower[window]["alpha"],
                bandpower[window]["beta"],
                ci,
                label
            ])

# Save AI input CSV
with open(OUT_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Alpha", "Beta", "CI", "Label"])
    writer.writerows(rows)

print("features_labels.csv created successfully.")
```

Run:

```bash
python make_features_labels.py
```

---

# ✅ FINAL CHECK (DO THIS BEFORE TRAINING AI)

Open `features_labels.csv` and confirm:

* No empty values
* Labels are only: `Calm`, `Neutral`, `Not Calm`
* CI ≈ Alpha / Beta
* Data count > 30 rows (minimum)

If yes → AI training is **legitimate**.

---

# 🧠 VIVA ONE-LINER (MEMORIZE)

> “The AI model was trained using Alpha power, Beta power, and the Calmness Index as features, with labels generated from a deterministic threshold-based calmness model.”

This sentence alone shows **you did not fake AI**.
