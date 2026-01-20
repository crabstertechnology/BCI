# TEST-3: Eyes Open vs Eyes Closed

## Overview

This test validates that the EEG system captures **true cortical activity** rather than only motion or muscle artifacts. The eyes-closed condition is known to increase rhythmic brain activity, preparing for alpha-band analysis.

This test is a **physiological sanity check**, not frequency-domain analysis.

---

## Folder Structure (Mandatory)

```text
EEG_Project/
├── data/
│   └── test3_eyes_open_closed/
│       ├── eyes_open.csv
│       ├── eyes_closed.csv
│       ├── comparison_plot.png
│       └── stats.txt
└── scripts/
    └── test3_eyes_open_closed.py
```

Folder consistency across tests ensures experimental credibility.

---

## Subject Protocol (Report-Ready)

**Instructions given to subject:**

1. Sit comfortably and remain still
2. Minimize facial and body movement
3. Keep **eyes open** for 20 seconds
4. Rest for 5 seconds
5. Keep **eyes closed** for 20 seconds
6. Do not fall asleep

These conditions isolate physiological differences between visual states.

---

## Eyes Open vs Eyes Closed Acquisition Script

**File:** `scripts/test3_eyes_open_closed.py`

**Important:** Close Arduino Serial Monitor before running.

```python
import serial
import numpy as np
import matplotlib.pyplot as plt
import time
import csv
import os

# ---------------- USER SETTINGS ----------------
PORT = 'COM5'          # Update according to system
BAUD_RATE = 115200
ADC_MAX = 4095
VREF = 3.3
FS = 250
DURATION = 20          # seconds per condition
SAVE_PATH = "../data/test3_eyes_open_closed/"
# ------------------------------------------------

os.makedirs(SAVE_PATH, exist_ok=True)

def record_eeg(label):
    ser = serial.Serial(PORT, BAUD_RATE)
    time.sleep(2)

    eeg = []
    timestamps = []

    print(f"Recording: {label}")
    start_time = time.time()

    while len(eeg) < FS * DURATION:
        if ser.in_waiting:
            raw = ser.readline().decode(errors="ignore").strip()
            if raw.isdigit():
                adc = int(raw)
                voltage = (adc / ADC_MAX) * VREF
                eeg.append(voltage)
                timestamps.append(time.time() - start_time)

    ser.close()
    return np.array(timestamps), np.array(eeg)

# -------- EYES OPEN --------
input("Press ENTER and keep EYES OPEN...")
t_open, eeg_open = record_eeg("Eyes Open")

# -------- PAUSE --------
print("Relax for 5 seconds...")
time.sleep(5)

# -------- EYES CLOSED --------
input("Press ENTER and keep EYES CLOSED...")
t_closed, eeg_closed = record_eeg("Eyes Closed")

# -------- SAVE DATA --------
def save_csv(filename, t, eeg):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Time (s)", "Voltage (V)"])
        for ti, vi in zip(t, eeg):
            writer.writerow([ti, vi])

save_csv(SAVE_PATH + "eyes_open.csv", t_open, eeg_open)
save_csv(SAVE_PATH + "eyes_closed.csv", t_closed, eeg_closed)

# -------- PLOT --------
plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1)
plt.plot(t_open, eeg_open, linewidth=0.8)
plt.title("Eyes Open – Raw EEG")
plt.ylabel("Voltage (V)")
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(t_closed, eeg_closed, linewidth=0.8)
plt.title("Eyes Closed – Raw EEG")
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.grid(True)

plt.tight_layout()
plt.savefig(SAVE_PATH + "comparison_plot.png", dpi=300)
plt.show()

# -------- STATS --------
with open(SAVE_PATH + "stats.txt", "w") as f:
    f.write("TEST-3: EYES OPEN vs EYES CLOSED\n")
    f.write("--------------------------------\n")
    f.write(f"Eyes Open  - Std Dev : {np.std(eeg_open):.6f} V\n")
    f.write(f"Eyes Closed- Std Dev : {np.std(eeg_closed):.6f} V\n")

print("Test-3 completed.")
print("Files saved to:", SAVE_PATH)
```

---

## Result Interpretation

### Visual Inspection (Primary Criterion)

**PASS if:**

* Eyes-closed signal appears more rhythmic
* Oscillations are slightly larger and smoother
* Reduced random jitter compared to eyes-open

**FAIL if:**

* Both signals appear visually identical
* Only noise or flat signals are present

---

### Statistical Observation (Secondary)

* Eyes-closed standard deviation is **often slightly higher**
* This is supportive, not definitive
* Do **not** draw conclusions from stats alone

Time-domain behavior matters here.

---

## Generated Evidence

* `eyes_open.csv` — raw eyes-open EEG
* `eyes_closed.csv` — raw eyes-closed EEG
* `comparison_plot.png` — visual comparison
* `stats.txt` — basic quantitative summary

This establishes **physiological contrast**, not spectral analysis.

---

## Report-Ready Statement

> “A comparative EEG recording under eyes-open and eyes-closed conditions showed increased rhythmic activity during the eyes-closed state, indicating readiness for alpha rhythm analysis.”

---

## Progress Gate (Strict)

You may proceed **only if**:

* Test-2 (blink artifacts) clearly passed
* Eyes-closed condition visually differs from eyes-open
* No clipping, saturation, or flat signals are present

If any condition fails, stop and fix the hardware.
