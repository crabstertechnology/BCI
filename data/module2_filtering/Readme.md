# 📦 MODULE-2: SIGNAL PROCESSING

## Band-Pass (0.5–40 Hz) + 50 Hz Notch Filter

---

## 🎯 What this module does (in one line)

It removes **DC drift, motion noise, and power-line interference**, leaving only EEG-relevant frequencies.

---

## 📁 Folder structure (extend your project)

```
EEG_Project/
│
├── data/
│   └── module2_filtering/
│       ├── raw_input.csv
│       ├── filtered_output.csv
│       ├── time_domain_plot.png
│       ├── frequency_plot.png
│       └── filter_stats.txt
│
└── scripts/
    └── module2_filtering.py
```

---

## ⚠️ IMPORTANT INPUT REQUIREMENT

Use **clean recorded data** from:

* Test-1, Test-2, or Test-3
  Preferably **eyes-closed data**.

👉 Copy one CSV and rename it as:

```
raw_input.csv
```

Place it inside:

```
data/module2_filtering/
```

---

## 🧪 Python Code — Band-Pass + Notch (FULL)

👉 Save as
`scripts/module2_filtering.py`

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, iirnotch, welch
import csv
import os

# ---------------- SETTINGS ----------------
FS = 250                 # Sampling rate (Hz)
LOWCUT = 0.5
HIGHCUT = 40.0
NOTCH_FREQ = 50.0        # India mains
Q = 30.0                 # Notch quality factor

DATA_PATH = "../data/module2_filtering/"
RAW_FILE = DATA_PATH + "raw_input.csv"
# ------------------------------------------

os.makedirs(DATA_PATH, exist_ok=True)

# -------- LOAD RAW DATA --------
time_vals = []
signal = []

with open(RAW_FILE, "r") as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        time_vals.append(float(row[0]))
        signal.append(float(row[1]))

signal = np.array(signal)
time_vals = np.array(time_vals)

# -------- BANDPASS FILTER --------
def bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype="band")
    return filtfilt(b, a, data)

# -------- NOTCH FILTER --------
def notch_filter(data, notch_freq, fs, q):
    nyq = 0.5 * fs
    w0 = notch_freq / nyq
    b, a = iirnotch(w0, q)
    return filtfilt(b, a, data)

# Apply filters
bandpassed = bandpass_filter(signal, LOWCUT, HIGHCUT, FS)
filtered = notch_filter(bandpassed, NOTCH_FREQ, FS, Q)

# -------- SAVE FILTERED DATA --------
with open(DATA_PATH + "filtered_output.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Time (s)", "Filtered Voltage (V)"])
    for t, v in zip(time_vals, filtered):
        writer.writerow([t, v])

# -------- TIME DOMAIN PLOT --------
plt.figure(figsize=(12,5))
plt.plot(time_vals, signal, label="Raw EEG", alpha=0.6)
plt.plot(time_vals, filtered, label="Filtered EEG", linewidth=1)
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title("EEG Signal Before and After Filtering")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(DATA_PATH + "time_domain_plot.png", dpi=300)
plt.show()

# -------- FREQUENCY DOMAIN (PSD) --------
f_raw, pxx_raw = welch(signal, FS, nperseg=1024)
f_filt, pxx_filt = welch(filtered, FS, nperseg=1024)

plt.figure(figsize=(10,5))
plt.semilogy(f_raw, pxx_raw, label="Raw EEG")
plt.semilogy(f_filt, pxx_filt, label="Filtered EEG")
plt.xlim(0, 60)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Power")
plt.title("Power Spectral Density Before and After Filtering")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(DATA_PATH + "frequency_plot.png", dpi=300)
plt.show()

# -------- STATS --------
with open(DATA_PATH + "filter_stats.txt", "w") as f:
    f.write("MODULE-2: SIGNAL FILTERING RESULTS\n")
    f.write("---------------------------------\n")
    f.write(f"Band-pass range : {LOWCUT}–{HIGHCUT} Hz\n")
    f.write(f"Notch frequency : {NOTCH_FREQ} Hz\n")
    f.write(f"Raw Std Dev     : {np.std(signal):.6f} V\n")
    f.write(f"Filtered Std Dev: {np.std(filtered):.6f} V\n")

print("Module-2 filtering completed.")
print("Outputs saved in:", DATA_PATH)
```

---

## 👀 HOW TO VERIFY IT WORKED (CRITICAL)

### Time-domain plot

**PASS if:**

* Slow drift removed
* Signal looks smoother
* Blinks still visible but less harsh

---

### Frequency-domain plot (MOST IMPORTANT)

**PASS if:**

* Clear dip at **50 Hz**
* Energy concentrated below **40 Hz**
* Reduced high-frequency noise

If 50 Hz spike is still strong → grounding problem.

---

## 📊 What you now have (report-ready evidence)

You now have:

* Raw vs filtered waveform plot
* PSD plot proving 50 Hz removal
* CSV of filtered EEG
* Filter configuration & stats

This is **core engineering validation**.

---

## 📝 Report sentence (use this)

> “The raw EEG signal was processed using a 0.5–40 Hz band-pass filter and a 50 Hz notch filter to remove motion artifacts and power-line interference, resulting in a cleaner signal suitable for feature extraction.”

---

## 🚫 DO NOT DO YET

Do NOT:

* Compute Alpha/Beta
* Train AI
* Claim mental states

Filtering comes **before** interpretation.
