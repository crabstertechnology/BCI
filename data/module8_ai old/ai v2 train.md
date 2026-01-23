Good — this is **exactly the right diagnosis step**.
If your real-time system predicts **only “Calm”**, that is **not a runtime bug**.
It is **almost always a training/data problem**.

I’ll do this in **strict order**:

1️⃣ Explain **why this is happening** (based on your two CSVs)
2️⃣ Define **what must change in training** (no theory fluff)
3️⃣ Give you **NEW, corrected AI training code** (Module-8 v2)
➡️ I will **NOT** jump to Module-9 yet (as you asked)

---

# 1️⃣ WHY YOUR AI IS ONLY PREDICTING “CALM”

Based on what you described and what usually appears in these projects, the issue is **one (or more) of these**:

---

## ❌ Problem A: Class imbalance (MOST LIKELY)

Your `features_labels.csv` probably looks like this internally:

| Label    | Approx count |
| -------- | ------------ |
| Calm     | 70–90%       |
| Neutral  | 5–20%        |
| Not Calm | 0–10%        |

If **Not Calm** samples are few or missing:

👉 Logistic Regression learns:

> “Always predict Calm → high accuracy”

This is **mathematically correct behavior**, but useless.

---

## ❌ Problem B: Features not separable

Your features may be **too correlated**:

* Alpha ↑
* Beta ↓
* CI ↑

So all points lie in a tight cluster → model cannot learn boundaries.

---

## ❌ Problem C: CI already encodes the label

You used **CI to generate labels**
and then used **CI again as an input feature**.

That creates **label leakage**.

Result:

* Model collapses to dominant class
* Appears “confident” but dumb

---

# 2️⃣ WHAT WE MUST CHANGE (NON-NEGOTIABLE)

To fix this **properly**, we will:

### ✅ Change 1: Remove CI from training features

CI is a **derived decision metric**, not a raw feature.

AI should learn from:

* Alpha power
* Beta power
* (optionally) Alpha/Beta ratio computed internally

But **NOT CI used to label data**.

---

### ✅ Change 2: Collapse labels to 2 classes (for stability)

For real-time biofeedback, **3 classes is fragile**.

We will use:

| Original | New      |
| -------- | -------- |
| Calm     | Calm     |
| Neutral  | Not Calm |
| Not Calm | Not Calm |

This dramatically improves learning.

---

### ✅ Change 3: Balance the classes

We will use:

* `class_weight="balanced"`
  OR
* Manual resampling

This is **mandatory**.

---

# 3️⃣ NEW TRAINING DESIGN (MODULE-8 v2)

## 🎯 Final training setup

**Features used**

```
[Alpha, Beta, Alpha/Beta]
```

**Labels**

```
Calm
Not Calm
```

**Model**

```
Logistic Regression (balanced)
```

This is:

* Interpretable
* Stable
* Defendable in viva

---

# 4️⃣ NEW TRAINING CODE (USE THIS)

👉 Save as
`scripts/module8_ai_training_v2.py`

This code **replaces your old training code**.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

# ---------------- PATHS ----------------
DATA_PATH = "../data/module8_ai/"
INPUT_FILE = DATA_PATH + "features_labels.csv"
# --------------------------------------

os.makedirs(DATA_PATH, exist_ok=True)

# -------- LOAD DATA --------
data = pd.read_csv(INPUT_FILE)

# -------- CLEAN & RECODE LABELS --------
# Collapse to binary classification
data["Label"] = data["Label"].replace({
    "Neutral": "Not Calm",
    "Not Calm": "Not Calm",
    "Calm": "Calm"
})

# -------- FEATURES (NO CI LEAKAGE) --------
data["AlphaBetaRatio"] = data["Alpha"] / data["Beta"]

X = data[["Alpha", "Beta", "AlphaBetaRatio"]]
y = data["Label"]

# -------- SCALE --------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -------- TRAIN / TEST SPLIT --------
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y,
    test_size=0.3,
    random_state=42,
    stratify=y
)

# -------- MODEL (BALANCED) --------
model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)

model.fit(X_train, y_train)

# -------- EVALUATION --------
y_pred = model.predict(X_test)

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
disp = ConfusionMatrixDisplay(cm, display_labels=model.classes_)
disp.plot()
plt.title("Confusion Matrix – Calm vs Not Calm")
plt.tight_layout()
plt.savefig(DATA_PATH + "confusion_matrix_v2.png", dpi=300)
plt.show()

# -------- SAVE MODEL --------
joblib.dump(model, DATA_PATH + "model_v2.pkl")
joblib.dump(scaler, DATA_PATH + "scaler_v2.pkl")

# -------- SAVE NOTES --------
with open(DATA_PATH + "training_notes_v2.txt", "w") as f:
    f.write("AI TRAINING – VERSION 2\n")
    f.write("----------------------\n")
    f.write("Model          : Logistic Regression\n")
    f.write("Classes        : Calm, Not Calm\n")
    f.write("Features       : Alpha, Beta, Alpha/Beta\n")
    f.write("CI used only for labeling (not as feature)\n")
    f.write("Class balance  : Enabled\n")

print("\nTraining completed. New model saved.")
```

---

# 5️⃣ WHAT RESULTS YOU SHOULD EXPECT NOW

### ✅ During training

* Confusion matrix shows **both classes predicted**
* Recall for *Not Calm* is **non-zero**
* Accuracy may DROP slightly → this is GOOD

### ✅ During real-time use

* Calm when relaxed
* **Not Calm appears during movement / talking**
* Fewer “always calm” outputs

---

# 6️⃣ VIVA-SAFE EXPLANATION (MEMORIZE)

> “The AI model was retrained using balanced binary classification and leakage-free features to avoid bias toward the dominant calm class and improve real-time responsiveness.”

That sentence alone explains **everything**.

---

## 🔜 NEXT (CONFIRM BEFORE MOVING ON)

**Do this first:**

1. Run `module8_ai_training_v2.py`
2. Confirm:

   * `model_v2.pkl`
   * `scaler_v2.pkl`
   * Confusion matrix shows both classes

Then say:

> **“Training v2 done, give Module-9 updated code”**

Do **NOT** jump ahead before this.
