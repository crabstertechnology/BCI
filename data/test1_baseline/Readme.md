
# TEST-1: Baseline Stability

## Overview

This test verifies baseline EEG signal stability under resting, eyes-open conditions.
It establishes signal validity before performing artifact or cognitive tests.

---

## Step 0 — Folder Structure (Mandatory)

Create the following structure **before running any code**:

```text
EEG_Project/
├── data/
│   └── test1_baseline/
│       ├── raw_data.csv
│       ├── baseline_plot.png
│       └── stats.txt
└── scripts/
    └── test1_baseline.py
```

This structure ensures reproducibility and professional project organization.

---

## Step 1 — Subject Instructions (Report-Ready)

**Instructions given to subject:**

* Sit comfortably
* Eyes open
* No body or facial movement
* Normal breathing
* Duration: **60 seconds**

These conditions minimize motion and muscle artifacts.

---

## Step 2 — Baseline Acquisition Script

**File:** `scripts/test1_baseline.py`

**Important:** Close Arduino Serial Monitor before execution.

```python
import serial
import numpy as np
import matplotlib.pyplot as plt
import time
import csv
import os

# ---------------- USER SETTINGS ----------------
PORT = 'COM5'          # Change according to system
BAUD_RATE = 115200
ADC_MAX = 4095         # 12-bit ADC
VREF = 3.3
FS = 250               # Sampling rate (Hz)
DURATION = 60          # Recording time (seconds)
SAVE_PATH = "../data/test1_baseline/"
# ------------------------------------------------

os.makedirs(SAVE_PATH, exist_ok=True)

ser = serial.Serial(PORT, BAUD_RATE)
time.sleep(2)

samples = FS * DURATION
eeg = []
timestamps = []

print("TEST-1: Baseline Stability Test")
print("Sit still, eyes open, breathe normally...")

start_time = time.time()

while len(eeg) < samples:
    if ser.in_waiting:
        raw = ser.readline().decode(errors='ignore').strip()
        if raw.isdigit():
            adc = int(raw)
            voltage = (adc / ADC_MAX) * VREF
            eeg.append(voltage)
            timestamps.append(time.time() - start_time)

ser.close()

eeg = np.array(eeg)
timestamps = np.array(timestamps)

# ---------------- SAVE RAW DATA ----------------
with open(SAVE_PATH + "raw_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Time (s)", "Voltage (V)"])
    for t, v in zip(timestamps, eeg):
        writer.writerow([t, v])

# ---------------- PLOT ----------------
plt.figure(figsize=(12, 4))
plt.plot(timestamps, eeg, linewidth=0.8)
plt.title("Baseline EEG Signal (Eyes Open)")
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.grid(True)
plt.tight_layout()
plt.savefig(SAVE_PATH + "baseline_plot.png", dpi=300)
plt.show()

# ---------------- STATISTICS ----------------
mean_v = np.mean(eeg)
std_v = np.std(eeg)
min_v = np.min(eeg)
max_v = np.max(eeg)

with open(SAVE_PATH + "stats.txt", "w") as f:
    f.write("TEST-1: BASELINE STABILITY RESULTS\n")
    f.write("--------------------------------\n")
    f.write(f"Duration        : {DURATION} seconds\n")
    f.write(f"Sampling Rate   : {FS} Hz\n")
    f.write(f"Mean Voltage    : {mean_v:.6f} V\n")
    f.write(f"Std Deviation   : {std_v:.6f} V\n")
    f.write(f"Min Voltage     : {min_v:.6f} V\n")
    f.write(f"Max Voltage     : {max_v:.6f} V\n")

print("Test completed.")
print(f"Data saved to: {SAVE_PATH}")
print(f"Std Deviation: {std_v:.6f} V")
```

---

## Step 3 — Generated Outputs

After execution, the following files are produced:

### `raw_data.csv`

* Time-stamped EEG voltage samples
* Serves as raw experimental evidence

### `baseline_plot.png`

* High-resolution time-domain EEG plot
* Suitable for reports and presentations

### `stats.txt`

* Mean, standard deviation, minimum, and maximum voltage values
* Quantitative signal stability metrics

---

## Step 4 — Pass / Fail Criteria

**PASS if:**

* Signal shows smooth low-amplitude fluctuations
* Standard deviation ≈ **0.005 – 0.03 V**
* No clipping at 0 V or 3.3 V

**FAIL if:**

* Flat-line signal
* Large random spikes
* Constant maximum or minimum values

If failed, inspect electrode placement, grounding, and power supply noise.

---

## Report-Ready Statement

> “A 60-second baseline EEG recording was acquired under eyes-open resting conditions. The signal exhibited stable low-amplitude fluctuations without saturation. Raw data, plots, and statistical metrics were stored for validation.”

---

## Discipline Rule (Non-Negotiable)

For every future experiment:

* Raw data must be saved
* Plot must be generated
* Statistics must be recorded

If it’s not saved, **it didn’t happen**.
