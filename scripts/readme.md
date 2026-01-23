Good choice. This step is **crucial**, and doing it properly will fix the “always Calm / always Not Calm” behavior **for real**, not by hacks.

I’ll give you a **clean, examiner-safe calibration protocol** that matches your hardware, code, and claims.

No theory fluff. Just **what to do, how long, and why**.

---

# 🧠 PROPER CALIBRATION DATA COLLECTION

*(For EEG Calmness AI – Single User)*

This calibration is **NOT optional** in EEG systems.
Anyone who skips it gets unstable models.

---

## 🎯 Goal of Calibration (be clear)

You are **not teaching the AI emotions**.
You are teaching it **what “calm” and “not calm” look like for THIS user**.

EEG is **person-specific**. Calibration solves that.

---

## 🧪 OVERALL PLAN (HIGH LEVEL)

You will collect **two short sessions**:

| Session | Purpose             | Label    |
| ------- | ------------------- | -------- |
| Relaxed | Define calm EEG     | Calm     |
| Active  | Define non-calm EEG | Not Calm |

Then:

* Extract Alpha/Beta features
* Build training CSV
* Retrain AI

---

## ⏱️ TOTAL TIME REQUIRED

**15–20 minutes total**

That’s realistic and defendable.

---

# 🔵 SESSION 1 — RELAXED CALIBRATION (CALM)

### 🧘 Instructions to user

* Sit comfortably
* Back supported
* Feet flat on floor
* Hands on thighs
* No talking
* Minimal movement

### 👀 Eyes

* Eyes **closed** (important)

### 🌬️ Breathing

* Slow nasal breathing
* ~5–6 breaths per minute
* No forced breath holding

### ⏱️ Duration

* **5 minutes** continuous

### ❌ Avoid

* Jaw clenching
* Swallowing repeatedly
* Adjusting electrodes

---

### 🧠 What this captures

* Higher Alpha
* Lower Beta
* Stable Alpha/Beta ratio

This becomes your **true Calm reference**.

---

# 🔴 SESSION 2 — ACTIVE CALIBRATION (NOT CALM)

### 🧠 Task options (pick ONE)

Choose **one**, don’t mix.

**Option A: Mental arithmetic**

* Serial subtraction (e.g., 100 − 7 repeatedly)

**Option B: Reading aloud**

* Read a technical paragraph softly

**Option C: Phone interaction**

* Scroll + read messages (light movement)

---

### 👀 Eyes

* Eyes **open**

### 🗣️ Movement

* Mild head / facial movement allowed
* No exaggerated motion

### ⏱️ Duration

* **5 minutes**

---

### 🧠 What this captures

* Increased Beta
* Reduced Alpha dominance
* Lower Alpha/Beta ratio

This becomes your **Not Calm reference**.

---

# 📊 WHAT DATA YOU MUST SAVE (MANDATORY)

For **both sessions**, save:

1. Raw EEG (optional)
2. Filtered EEG
3. Sliding-window:

   * Alpha power
   * Beta power
   * Alpha/Beta ratio

Your existing pipeline already does this.

---

## 📁 FILE NAMING (VERY IMPORTANT)

Use **clear separation**:

```
data/calibration/
├── calm_session_bandpower.csv
└── not_calm_session_bandpower.csv
```

This avoids label confusion later.

---

# 🏷️ LABELING RULE (STRICT)

| File                           | Label    |
| ------------------------------ | -------- |
| calm_session_bandpower.csv     | Calm     |
| not_calm_session_bandpower.csv | Not Calm |

Do **not** label window-by-window manually.
Label by **session intent**.

This is standard in BCI.

---

# 🧪 HOW MUCH DATA IS ENOUGH?

With:

* 2-sec window
* 0.5-sec step
* 5 minutes

You get ≈ **500 windows per class**.

That’s **more than enough** for Logistic Regression.

---

# 🚫 COMMON MISTAKES (DO NOT DO THESE)

❌ Mixing calm and active in one session
❌ Talking during calm session
❌ Training AI on one session only
❌ Using thresholds from old data

Any of these will break consistency.

---

# 🧠 HOW TO EXPLAIN THIS IN VIVA (MEMORIZE)

> “Calibration data was collected through controlled relaxed and cognitively active sessions to establish subject-specific EEG feature distributions before AI training.”

That sentence = **full marks**.

---

## 🔜 WHAT’S NEXT (CHOOSE ONE)

Now that you know **how to collect calibration data**, choose:

1️⃣ **Give script to record calibration sessions separately**
2️⃣ **Give script to merge calibration data into training CSV**
3️⃣ **Explain how to justify calibration in the report**

Reply with **1, 2, or 3 only**.
Perfect. We’ll do this **cleanly and in the correct order**.

You asked for **two things**:
1️⃣ **Arduino code first**
2️⃣ **Then a Python script to record calibration data**

No AI yet. No FFT yet. Just **solid data capture**.

---

# 1️⃣ ARDUINO CODE (DATA ACQUISITION ONLY)

This code does **one job**:

* Read EEG analog signal
* Stream **raw ADC values** over Serial
* At a **stable sampling rate (~250 Hz)**

### ✅ Assumptions

* You’re using **Arduino UNO R4 Minima**
* BioAmp EXG Pill output → **A0**
* Baud rate: **115200**

---

## 🔧 Arduino Sketch (UPLOAD THIS)

```cpp
// ===============================
// EEG Raw Data Streaming
// Arduino UNO R4 Minima
// ===============================

const int EEG_PIN = A0;
const unsigned long SAMPLE_INTERVAL_US = 4000; // ~250 Hz (1/250s)

unsigned long lastSampleTime = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial); // wait for serial
}

void loop() {
  unsigned long now = micros();

  if (now - lastSampleTime >= SAMPLE_INTERVAL_US) {
    lastSampleTime = now;

    int adcValue = analogRead(EEG_PIN);
    Serial.println(adcValue);
  }
}
```

---

## ✅ HOW TO VERIFY ARDUINO SIDE

1. Upload code
2. Open **Serial Monitor**
3. Set baud rate to **115200**
4. You should see:

   ```
   2048
   2053
   2039
   ...
   ```

If numbers are changing → **Arduino side is DONE**.

❌ Do NOT apply filtering or FFT on Arduino.

---

# 2️⃣ PYTHON SCRIPT — CALIBRATION DATA RECORDING

This script will:

* Read serial data
* Timestamp it
* Save **raw EEG** to CSV
* You will run it **once per session** (Calm / Not Calm)

---

## 📁 OUTPUT FILES (CREATED BY SCRIPT)

Example:

```
data/calibration/
├── calm_raw.csv
└── not_calm_raw.csv
```

Format:

```csv
Time(s),ADC
0.004,2048
0.008,2052
...
```

---

## 🧪 PYTHON SCRIPT (RAW EEG LOGGER)

👉 Save as
`scripts/record_calibration_raw.py`

```python
import serial
import time
import csv
import os

# ---------------- SETTINGS ----------------
PORT = "COM6"          # 🔴 change if needed
BAUD = 115200
DURATION_SEC = 300     # 5 minutes per session
SAVE_PATH = "../data/calibration/"
# -----------------------------------------

os.makedirs(SAVE_PATH, exist_ok=True)

# -------- ASK USER --------
session = input("Enter session name (calm / not_calm): ").strip().lower()
filename = SAVE_PATH + f"{session}_raw.csv"

# -------- SERIAL --------
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

print(f"\nRecording '{session}' session for {DURATION_SEC} seconds...")
print("Press CTRL+C to stop early.\n")

start_time = time.time()

with open(filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Time(s)", "ADC"])

    try:
        while time.time() - start_time < DURATION_SEC:
            if ser.in_waiting:
                raw = ser.readline().decode(errors="ignore").strip()
                if raw.isdigit():
                    t = time.time() - start_time
                    writer.writerow([f"{t:.4f}", int(raw)])
    except KeyboardInterrupt:
        print("\nRecording stopped early by user.")

ser.close()
print(f"\nData saved to: {filename}")
```

---

## ✅ HOW TO USE THIS (STEP-BY-STEP)

### 🔵 Calm session

1. Wear electrodes
2. Sit relaxed, eyes closed
3. Run:

   ```bash
   python record_calibration_raw.py
   ```
4. Enter:

   ```
   calm
   ```
5. Stay still for ~5 minutes

---

### 🔴 Not-calm session

1. Eyes open
2. Do mental arithmetic / reading
3. Run again:

   ```bash
   python record_calibration_raw.py
   ```
4. Enter:

   ```
   not_calm
   ```

---

## 🧠 WHAT YOU HAVE AFTER THIS STEP

You now have:

* Clean **raw EEG recordings**
* Proper **session separation**
* Reproducible calibration data

This is **exactly how real EEG labs do it**.

---

## 🚫 DO NOT DO YET

* ❌ No filtering
* ❌ No FFT
* ❌ No AI training

We do those **after calibration capture**.

---

## 🔜 NEXT (CHOOSE ONE, DON’T SKIP ORDER)

Now choose the next step:

1️⃣ **Give Python script to filter these raw files**
2️⃣ **Give Python script to extract Alpha/Beta from calibration data**
3️⃣ **Explain how to document calibration in report**

Reply with **1, 2, or 3 only**.
