# 📊 MODULE-3: FFT & ALPHA / BETA BAND POWER CALCULATION

---

## 🎯 Objective (simple and honest)

Convert the **filtered EEG signal** into the frequency domain and quantify:

* **Alpha power (8–13 Hz)** → relaxation
* **Beta power (13–30 Hz)** → mental activity

No claims. Just measurable power.

---

## 📁 Folder Structure (extend your project)

```
EEG_Project/
│
├── data/
│   └── module3_fft_bandpower/
│       ├── filtered_input.csv
│       ├── fft_plot.png
│       ├── band_power.txt
│       └── band_power_bar.png
│
└── scripts/
    └── module3_fft_bandpower.py
```

---

## ⚠️ INPUT REQUIREMENT (IMPORTANT)

Use **filtered EEG output** from Module-2.

➡️ Copy:

```
filtered_output.csv
```

➡️ Rename it to:

```
filtered_input.csv
```

➡️ Place it inside:

```
data/module3_fft_bandpower/
```

---

## 🧪 Python Code — FFT + Alpha/Beta Power (FULL)

👉 Save as
`scripts/module3_fft_bandpower.py`

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
import csv
import os

# ---------------- SETTINGS ----------------
FS = 250                 # Sampling rate (Hz)
ALPHA_BAND = (8, 13)
BETA_BAND = (13, 30)

DATA_PATH = "../data/module3_fft_bandpower/"
INPUT_FILE = DATA_PATH + "filtered_input.csv"
# ------------------------------------------

os.makedirs(DATA_PATH, exist_ok=True)

# -------- LOAD FILTERED EEG --------
signal = []

with open(INPUT_FILE, "r") as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        signal.append(float(row[1]))

signal = np.array(signal)

# -------- FFT USING WELCH PSD --------
freqs, psd = welch(signal, FS, nperseg=1024)

# -------- BAND POWER FUNCTION --------
def band_power(freqs, psd, band):
    idx = np.logical_and(freqs >= band[0], freqs <= band[1])
    return np.trapz(psd[idx], freqs[idx])

alpha_power = band_power(freqs, psd, ALPHA_BAND)
beta_power = band_power(freqs, psd, BETA_BAND)
alpha_beta_ratio = alpha_power / beta_power if beta_power != 0 else 0

# -------- SAVE RESULTS --------
with open(DATA_PATH + "band_power.txt", "w") as f:
    f.write("MODULE-3: FFT & BAND POWER RESULTS\n")
    f.write("---------------------------------\n")
    f.write(f"Alpha Band (8–13 Hz) Power : {alpha_power:.6e}\n")
    f.write(f"Beta Band (13–30 Hz) Power : {beta_power:.6e}\n")
    f.write(f"Alpha/Beta Ratio          : {alpha_beta_ratio:.4f}\n")

# -------- FFT PLOT --------
plt.figure(figsize=(10,5))
plt.semilogy(freqs, psd)
plt.axvspan(8, 13, color='green', alpha=0.3, label='Alpha Band')
plt.axvspan(13, 30, color='red', alpha=0.3, label='Beta Band')
plt.xlim(0, 40)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Power")
plt.title("EEG Power Spectral Density (FFT)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(DATA_PATH + "fft_plot.png", dpi=300)
plt.show()

# -------- BAR GRAPH --------
plt.figure(figsize=(6,4))
plt.bar(["Alpha Power", "Beta Power"], [alpha_power, beta_power])
plt.ylabel("Power")
plt.title("Alpha vs Beta Band Power")
plt.tight_layout()
plt.savefig(DATA_PATH + "band_power_bar.png", dpi=300)
plt.show()

print("Module-3 FFT & Band Power completed.")
print(f"Alpha Power      : {alpha_power:.6e}")
print(f"Beta Power       : {beta_power:.6e}")
print(f"Alpha/Beta Ratio : {alpha_beta_ratio:.4f}")
```

---

## 👀 HOW TO INTERPRET RESULTS (DO NOT OVERTHINK)

### ✅ What a **good result** looks like

* PSD concentrated **below 30–40 Hz**
* Clear energy in **8–13 Hz (Alpha)** for eyes-closed data
* Alpha/Beta ratio:

  * **Higher** → more relaxed
  * **Lower** → more active thinking

### ❌ Red flags

* Huge power at 50 Hz → notch filter failed
* Flat PSD → dead signal
* Beta power dominating during eyes-closed → noisy data

---

## 📊 What you now have (EXAMINER-READY)

You now have:

* `fft_plot.png` → frequency evidence
* `band_power_bar.png` → easy comparison
* `band_power.txt` → numeric proof

This is **real EEG analysis**, not buzzwords.

---

## 📝 Report-ready explanation (use this)

> “The filtered EEG signal was transformed into the frequency domain using Welch’s power spectral density estimation. Alpha (8–13 Hz) and Beta (13–30 Hz) band powers were computed, and the Alpha/Beta ratio was used as an indicator of relaxation versus mental activity.”

---

## 🚫 IMPORTANT LIMITATION (STATE THIS)

* Band power is **relative**, not absolute
* Valid only for **same user comparisons**
* Not a medical metric

This makes your project **honest and defendable**.
