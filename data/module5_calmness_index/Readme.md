# 🧘 MODULE-5: CALMNESS INDEX & THRESHOLDING (NO AI)

---

## 🎯 What this module does (in plain terms)

It converts EEG band features into a **single numerical score** that represents how calm the user is **relative to their own baseline**.

* No AI
* No labels like “emotion”
* No medical claims

Just **signal → number → interpretation**.

---

## 1️⃣ Calmness Index — Definition (USE THIS)

### Core idea

Calmness increases when:

* **Alpha power increases**
* **Beta power decreases**

### Final formula (simple, accepted, explainable)

[
\textbf{Calmness Index (CI)} = \frac{\text{Alpha Power}}{\text{Beta Power}}
]

Why this works:

* Dimensionless
* Robust to amplitude scaling
* Widely used in EEG biofeedback

---

## 2️⃣ Personal Baseline (MANDATORY)

Absolute values are meaningless across users.
So we normalize **per user**.

### Baseline recording

Use **eyes-closed relaxed data** (20–30 seconds).

Compute:

* Mean Calmness Index → μ
* Standard deviation → σ

These define **this user’s normal calm state**.

---

## 3️⃣ Thresholding Logic (NO GUESSWORK)

Define thresholds like this:

| State        | Condition      |
| ------------ | -------------- |
| **Calm**     | CI ≥ μ         |
| **Neutral**  | μ − σ ≤ CI < μ |
| **Not Calm** | CI < μ − σ     |

This is:

* Simple
* Statistically grounded
* Defendable in viva

---

## 4️⃣ Folder Structure

```
EEG_Project/
│
├── data/
│   └── module5_calmness_index/
│       ├── baseline_bandpower.txt
│       ├── calmness_timeline.csv
│       ├── calmness_plot.png
│       └── thresholds.txt
│
└── scripts/
    └── module5_calmness_index.py
```

---

## 5️⃣ Input Requirement

You must already have:

* Alpha power
* Beta power
  (from Module-3 or Module-4)

We’ll assume **time-windowed band power** (e.g., every 2 seconds).

---

## 6️⃣ Python Code — Calmness Index + Thresholding

👉 Save as
`scripts/module5_calmness_index.py`

```python
import numpy as np
import matplotlib.pyplot as plt
import csv
import os

# ---------------- SETTINGS ----------------
DATA_PATH = "../data/module5_calmness_index/"
WINDOWS = 30            # number of CI windows
# -----------------------------------------

os.makedirs(DATA_PATH, exist_ok=True)

# -------- SAMPLE INPUT (replace with real values) --------
# These should come from sliding-window Alpha/Beta computation
alpha_power = np.random.uniform(2.0, 4.0, WINDOWS)
beta_power  = np.random.uniform(1.0, 3.0, WINDOWS)

# -------- CALMNESS INDEX --------
calmness_index = alpha_power / beta_power

# -------- BASELINE (use first N windows as relaxed baseline) --------
baseline_ci = calmness_index[:10]
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
with open(DATA_PATH + "baseline_bandpower.txt", "w") as f:
    f.write("CALMNESS BASELINE\n")
    f.write("-----------------\n")
    f.write(f"Mean (μ)  : {mu:.4f}\n")
    f.write(f"Std (σ)   : {sigma:.4f}\n")

# -------- SAVE TIMELINE --------
with open(DATA_PATH + "calmness_timeline.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Window", "Calmness Index", "State"])
    for i, (ci, st) in enumerate(zip(calmness_index, states)):
        writer.writerow([i+1, ci, st])

# -------- PLOT --------
plt.figure(figsize=(10,4))
plt.plot(calmness_index, marker='o', label="Calmness Index")
plt.axhline(mu, linestyle="--", label="Baseline Mean")
plt.axhline(mu - sigma, linestyle=":", label="Lower Threshold")
plt.xlabel("Time Windows")
plt.ylabel("Calmness Index")
plt.title("Calmness Index Over Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(DATA_PATH + "calmness_plot.png", dpi=300)
plt.show()

# -------- SAVE THRESHOLDS --------
with open(DATA_PATH + "thresholds.txt", "w") as f:
    f.write("CALMNESS THRESHOLDS\n")
    f.write("------------------\n")
    f.write(f"Calm        : CI ≥ {mu:.4f}\n")
    f.write(f"Neutral     : {mu - sigma:.4f} ≤ CI < {mu:.4f}\n")
    f.write(f"Not Calm    : CI < {mu - sigma:.4f}\n")

print("Calmness Index computation completed.")
print(f"Baseline Mean: {mu:.4f}")
print(f"Baseline Std : {sigma:.4f}")
```

> ⚠️ In your **final integration**, replace the random values with **real sliding-window Alpha/Beta values**.

---

## 7️⃣ How to Interpret Results (IMPORTANT)

### ✅ Good behavior

* Calmness Index rises during relaxed breathing
* Drops during distraction or movement
* Threshold crossings make sense intuitively

### ❌ Bad behavior

* CI jumps randomly → noise problem
* CI always flat → feature extraction bug
* CI inverted → Alpha/Beta swapped

---

## 8️⃣ Report-Ready Explanation (USE THIS)

> “A Calmness Index was defined as the ratio of Alpha to Beta band power. User-specific baseline statistics were computed under relaxed conditions, and thresholding was applied to classify calm, neutral, and non-calm states without using machine learning.”

---

## 🔒 Why this step matters (brutal truth)

If someone asks:

> “Why do you even need AI?”

You can answer:

> “We don’t. The system already works deterministically. AI is added only to improve adaptability.”

That answer **wins marks**.
