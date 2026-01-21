# 📊 MODULE-4: ALPHA/BETA COMPARISON

## Eyes Open vs Eyes Closed

---

## 🎯 Objective (what this proves)

To demonstrate that:

* **Alpha power increases** when eyes are closed
* **Beta power decreases** when eyes are closed
* Alpha/Beta ratio is **higher in relaxed state**

This is **textbook EEG behavior**. If this works, your pipeline is valid.

---

## 📁 Folder Structure

```
EEG_Project/
│
├── data/
│   └── module4_alpha_beta_comparison/
│       ├── eyes_open_filtered.csv
│       ├── eyes_closed_filtered.csv
│       ├── psd_comparison.png
│       ├── bandpower_comparison.png
│       └── comparison_stats.txt
│
└── scripts/
    └── module4_alpha_beta_comparison.py
```

---

## ⚠️ INPUT REQUIREMENT (IMPORTANT)

From **Module-2 filtering output**:

* Take **eyes-open filtered data** → rename to

  ```
  eyes_open_filtered.csv
  ```
* Take **eyes-closed filtered data** → rename to

  ```
  eyes_closed_filtered.csv
  ```

Both files must be in:

```
data/module4_alpha_beta_comparison/
```

Format must be:

```
Time (s), Filtered Voltage (V)
```

---

## 🧪 Python Code — Alpha/Beta Comparison (FULL)

👉 Save as
`scripts/module4_alpha_beta_comparison.py`

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
import csv
import os

# ---------------- SETTINGS ----------------
FS = 250
ALPHA_BAND = (8, 13)
BETA_BAND = (13, 30)

DATA_PATH = "../data/module4_alpha_beta_comparison/"
OPEN_FILE = DATA_PATH + "eyes_open_filtered.csv"
CLOSED_FILE = DATA_PATH + "eyes_closed_filtered.csv"
# ------------------------------------------

def load_signal(filename):
    signal = []
    with open(filename, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            signal.append(float(row[1]))
    return np.array(signal)

def band_power(freqs, psd, band):
    idx = np.logical_and(freqs >= band[0], freqs <= band[1])
    return np.trapz(psd[idx], freqs[idx])

# -------- LOAD DATA --------
eeg_open = load_signal(OPEN_FILE)
eeg_closed = load_signal(CLOSED_FILE)

# -------- PSD --------
f_open, psd_open = welch(eeg_open, FS, nperseg=1024)
f_closed, psd_closed = welch(eeg_closed, FS, nperseg=1024)

# -------- BAND POWER --------
alpha_open = band_power(f_open, psd_open, ALPHA_BAND)
beta_open = band_power(f_open, psd_open, BETA_BAND)

alpha_closed = band_power(f_closed, psd_closed, ALPHA_BAND)
beta_closed = band_power(f_closed, psd_closed, BETA_BAND)

ratio_open = alpha_open / beta_open if beta_open != 0 else 0
ratio_closed = alpha_closed / beta_closed if beta_closed != 0 else 0

# -------- PSD COMPARISON PLOT --------
plt.figure(figsize=(10,5))
plt.semilogy(f_open, psd_open, label="Eyes Open")
plt.semilogy(f_closed, psd_closed, label="Eyes Closed")
plt.axvspan(8, 13, color='green', alpha=0.2, label="Alpha Band")
plt.axvspan(13, 30, color='red', alpha=0.2, label="Beta Band")
plt.xlim(0, 40)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Power")
plt.title("PSD Comparison: Eyes Open vs Eyes Closed")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(DATA_PATH + "psd_comparison.png", dpi=300)
plt.show()

# -------- BAR COMPARISON --------
labels = ["Alpha Open", "Alpha Closed", "Beta Open", "Beta Closed"]
values = [alpha_open, alpha_closed, beta_open, beta_closed]

plt.figure(figsize=(7,4))
plt.bar(labels, values)
plt.ylabel("Power")
plt.title("Alpha & Beta Band Power Comparison")
plt.tight_layout()
plt.savefig(DATA_PATH + "bandpower_comparison.png", dpi=300)
plt.show()

# -------- SAVE STATS --------
with open(DATA_PATH + "comparison_stats.txt", "w") as f:
    f.write("MODULE-4: ALPHA/BETA COMPARISON\n")
    f.write("--------------------------------\n")
    f.write(f"Alpha Power (Eyes Open)   : {alpha_open:.6e}\n")
    f.write(f"Alpha Power (Eyes Closed) : {alpha_closed:.6e}\n")
    f.write(f"Beta Power (Eyes Open)    : {beta_open:.6e}\n")
    f.write(f"Beta Power (Eyes Closed)  : {beta_closed:.6e}\n")
    f.write(f"Alpha/Beta (Eyes Open)   : {ratio_open:.4f}\n")
    f.write(f"Alpha/Beta (Eyes Closed) : {ratio_closed:.4f}\n")

print("Module-4 Alpha/Beta comparison completed.")
print(f"Alpha/Beta (Open)   : {ratio_open:.4f}")
print(f"Alpha/Beta (Closed) : {ratio_closed:.4f}")
```

---

## 👀 HOW TO INTERPRET RESULTS (THIS IS WHAT EXAMINERS WANT)

### ✅ Expected outcome

* **Alpha (eyes closed) > Alpha (eyes open)**
* **Beta (eyes open) ≥ Beta (eyes closed)**
* **Alpha/Beta ratio higher when eyes closed**

This confirms **relaxation physiology**.

---

## ❌ Red flags

* No difference → electrode or noise issue
* Beta dominates eyes-closed → muscle noise
* Huge 50 Hz peak → notch filter failed

---

## 📝 Report-ready explanation

> “A comparative analysis of Alpha and Beta band power revealed increased Alpha dominance during the eyes-closed condition, resulting in a higher Alpha/Beta ratio, which is consistent with relaxed cognitive states.”

---

## 🚦 CHECKPOINT

You are now **officially done with signal validation and feature extraction**.

Everything beyond this (calmness index, AI, feedback) is **legitimate**.
