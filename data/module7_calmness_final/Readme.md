# 🔗 CONNECT BANDPOWER CSV → CALMNESS INDEX (FINAL)

---

## 📌 What you already have (important)

From the previous module, you now have:

```
data/module6_bandpower_extraction/
└── bandpower_windows.csv
```

Format:

```csv
Window,Alpha_Power,Beta_Power
1,0.0000123,0.0000089
2,0.0000131,0.0000075
...
```

This is **REAL EEG-derived data**.

---

## 📁 New folder (keep things clean)

```
data/module7_calmness_final/
│
├── calmness_timeline.csv
├── calmness_plot.png
├── baseline.txt
└── thresholds.txt
```

---

## 🧪 FINAL CALMNESS INDEX CODE (REAL DATA)

👉 Save as
`scripts/module7_calmness_from_csv.py`

```python
import numpy as np
import matplotlib.pyplot as plt
import csv
import os

# ---------------- PATHS ----------------
INPUT_CSV = "../data/module6_bandpower_extraction/bandpower_windows.csv"
DATA_PATH = "../data/module7_calmness_final/"
# ---------------------------------------

os.makedirs(DATA_PATH, exist_ok=True)

# -------- LOAD BAND POWER DATA --------
windows = []
alpha_power = []
beta_power = []

with open(INPUT_CSV, "r") as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        windows.append(int(row[0]))
        alpha_power.append(float(row[1]))
        beta_power.append(float(row[2]))

alpha_power = np.array(alpha_power)
beta_power = np.array(beta_power)

# -------- CALMNESS INDEX --------
calmness_index = alpha_power / beta_power

# -------- BASELINE (FIRST N WINDOWS) --------
BASELINE_WINDOWS = 10   # relaxed calibration
baseline_ci = calmness_index[:BASELINE_WINDOWS]

mu = np.mean(baseline_ci)
sigma = np.std(baseline_ci)

# -------- THRESHOLDING --------
states = []
for ci in calmness_index:
    if ci >= mu:
        states.append("Calm")
    elif ci >= mu - sigma:
        states.append("Neutral")
    else:
        states.append("Not Calm")

# -------- SAVE BASELINE --------
with open(DATA_PATH + "baseline.txt", "w") as f:
    f.write("CALMNESS BASELINE\n")
    f.write("-----------------\n")
    f.write(f"Mean (mu)     : {mu:.6f}\n")
    f.write(f"Std (sigma)   : {sigma:.6f}\n")
    f.write(f"Baseline N    : {BASELINE_WINDOWS}\n")

# -------- SAVE TIMELINE CSV --------
with open(DATA_PATH + "calmness_timeline.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Window", "Alpha", "Beta", "Calmness_Index", "State"])
    for w, a, b, ci, st in zip(windows, alpha_power, beta_power, calmness_index, states):
        writer.writerow([w, a, b, ci, st])

# -------- SAVE THRESHOLDS --------
with open(DATA_PATH + "thresholds.txt", "w") as f:
    f.write("CALMNESS THRESHOLDS\n")
    f.write("------------------\n")
    f.write(f"Calm        : CI >= {mu:.6f}\n")
    f.write(f"Neutral     : {mu - sigma:.6f} <= CI < {mu:.6f}\n")
    f.write(f"Not Calm    : CI < {mu - sigma:.6f}\n")

# -------- PLOT --------
plt.figure(figsize=(10,4))
plt.plot(calmness_index, marker='o', label="Calmness Index")
plt.axhline(mu, linestyle="--", label="Baseline Mean")
plt.axhline(mu - sigma, linestyle=":", label="Lower Threshold")
plt.xlabel("Window Index")
plt.ylabel("Calmness Index")
plt.title("Calmness Index (Real EEG Data)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(DATA_PATH + "calmness_plot.png", dpi=300)
plt.show()

print("Calmness Index computed from REAL EEG data.")
print(f"Baseline Mean (mu)  : {mu:.6f}")
print(f"Baseline Std (sigma): {sigma:.6f}")
```

---

## ✅ HOW TO VERIFY (DON’T SKIP)

### 1️⃣ Check `calmness_timeline.csv`

You should see:

* CI values smoothly changing
* State transitions that make sense
* No NaNs or infinities

---

### 2️⃣ Check `calmness_plot.png`

Expected behavior:

* CI rises during relaxed periods
* CI drops during noisy or active periods
* Threshold lines correctly placed

If CI is chaotic → problem is earlier (filtering/electrodes).

---

## 🧠 HOW TO EXPLAIN THIS IN VIVA (MEMORIZE)

> “Alpha and Beta band powers computed from sliding-window FFT analysis were used to derive a Calmness Index, which was normalized using a personalized baseline and classified using statistical thresholds.”

This sentence alone **wins confidence**.

---

## 🔒 WHAT YOU HAVE NOW (BIG DEAL)

You have a **complete deterministic BCI pipeline**:

```
EEG → Filter → FFT → Alpha/Beta → Calmness → Feedback
```

No AI needed to prove validity.

---

## 🚫 DO NOT CLAIM

* Emotion detection
* Mental health diagnosis
* Mind reading

Your strength is **engineering discipline**.
