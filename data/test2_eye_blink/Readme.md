
# TEST-2: Eye Blink Artifact

## Overview

This test validates that the EEG acquisition chain (electrodes, amplifier, ADC, and data pipeline) is capable of capturing **real physiological activity**. Eye blinks produce large, predictable frontal artifacts and serve as a ground-truth validation signal.

Failure to detect eye blink artifacts indicates invalid EEG acquisition.

---

## Folder Structure (Do Not Modify)

```text
EEG_Project/
├── data/
│   └── test2_eye_blink/
│       ├── raw_data.csv
│       ├── blink_plot.png
│       └── stats.txt
└── scripts/
    └── test2_eye_blink.py
```

This structure must be preserved for reproducibility and reporting.

---

## Subject Protocol (Report-Ready)

**Instructions given to subject:**

1. Sit still and upright
2. Eyes open
3. Blink **hard** 3–5 times
4. Pause approximately 3 seconds between blinks
5. Total recording duration: **30 seconds**

No head movement. No speaking.

---

## Eye Blink Acquisition Script

**File:** `scripts/test2_eye_blink.py`

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
ADC_MAX = 4095         # 12-bit ADC
VREF = 3.3
FS = 250               # Sampling rate (Hz)
DURATION = 30          # Recording duration (seconds)
SAVE_PATH = "../data/test2_eye_blink/"
# ------------------------------------------------

os.makedirs(SAVE_PATH, exist_ok=True)

ser = serial.Serial(PORT, BAUD_RATE)
time.sleep(2)

samples = FS * DURATION
eeg = []
timestamps = []

print("TEST-2: Eye Blink Artifact Test")
print("Blink HARD 3–5 times. Pause between blinks.")

start_time = time.time()

while len(eeg) < samples:
    if ser.in_waiting:
        raw = ser.readline().decode(errors="ignore").strip()
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
plt.title("Eye Blink Artifact – Raw EEG Signal")
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.grid(True)
plt.tight_layout()
plt.savefig(SAVE_PATH + "blink_plot.png", dpi=300)
plt.show()

# ---------------- STATISTICS ----------------
mean_v = np.mean(eeg)
std_v = np.std(eeg)
peak_to_peak = np.max(eeg) - np.min(eeg)

with open(SAVE_PATH + "stats.txt", "w") as f:
    f.write("TEST-2: EYE BLINK ARTIFACT RESULTS\n")
    f.write("---------------------------------\n")
    f.write(f"Duration           : {DURATION} seconds\n")
    f.write(f"Sampling Rate      : {FS} Hz\n")
    f.write(f"Mean Voltage       : {mean_v:.6f} V\n")
    f.write(f"Std Deviation      : {std_v:.6f} V\n")
    f.write(f"Peak-to-Peak Value : {peak_to_peak:.6f} V\n")

print("Eye Blink Test completed.")
print(f"Data saved to: {SAVE_PATH}")
print(f"Peak-to-Peak: {peak_to_peak:.6f} V")
```

---

## Result Interpretation

### Visual Validation (Primary)

**PASS if:**

* Tall, sharp spikes appear in the signal
* Each spike corresponds to a blink
* Spike amplitudes are significantly larger than baseline fluctuations

**FAIL if:**

* No visible spikes
* Signal resembles baseline noise
* No temporal correlation with blinks

---

### Quantitative Validation

* Peak-to-peak amplitude must be **significantly higher** than Test-1 baseline
* Typically **2–5× larger** for BioAmp-based EEG systems

If this condition is not met, electrode placement, grounding, or power noise is incorrect.

---

## Generated Artifacts

The following files serve as experimental evidence:

* `raw_data.csv` — raw time-domain EEG samples
* `blink_plot.png` — visual confirmation of blink artifacts
* `stats.txt` — numerical amplitude validation

This is **engineering-grade validation**, not a demo.

---

## Report-Ready Statement

> “Eye blink artifacts were observed as high-amplitude transient spikes in the EEG signal, confirming correct electrode placement and functional signal acquisition.”

---

## Progress Gate (Strict)

You may proceed **only if**:

* Blink artifacts are clearly visible
* Peak-to-peak amplitude exceeds baseline by a wide margin

Otherwise, stop and fix the hardware.

