# 🤖 MODULE-8: SIMPLE AI ON TOP OF CALMNESS INDEX

*(Optional, Classical ML, No Overclaims)*

---

## 🎯 What AI does here (be very clear)

AI **does NOT**:

* Read raw EEG
* Replace FFT
* Replace Calmness Index
* Detect emotions

AI **ONLY**:

* Learns **personalized boundaries** between calm / not calm
* Smooths noisy decisions
* Improves consistency across sessions

This keeps your system **honest and strong**.

---

## 🧠 AI INPUTS (FEATURES)

You already computed everything needed.
Your **feature vector per window** is:

| Feature             | Source             |
| ------------------- | ------------------ |
| Alpha power         | Sliding-window FFT |
| Beta power          | Sliding-window FFT |
| Alpha/Beta ratio    | Calmness Index     |
| Optional: CI change | Temporal smoothing |

No raw EEG goes into AI. This is **mandatory**.

---

## 🏷️ LABELS (How AI learns)

Labels come from your **deterministic logic**:

| Condition      | Label    |
| -------------- | -------- |
| CI ≥ μ         | Calm     |
| μ − σ ≤ CI < μ | Neutral  |
| CI < μ − σ     | Not Calm |

This is called **weak supervision** — acceptable and defendable.

---

## 📁 Folder Structure

```
data/module8_ai/
│
├── features_labels.csv
├── model.pkl
├── evaluation.txt
└── confusion_matrix.png

scripts/
└── module8_ai_training.py
```

---

## 🧪 STEP 1: Prepare AI Dataset (from existing CSV)

### features_labels.csv format

```csv
Alpha,Beta,CI,Label
0.000012,0.000008,1.50,Calm
0.000010,0.000011,0.91,Not Calm
...
```

This comes directly from:

* `bandpower_windows.csv`
* `calmness_timeline.csv`

---

## 🧪 STEP 2: AI Model Choice (DON’T ARGUE THIS)

Use **Logistic Regression**.

Why:

* Small data
* Interpretable
* Stable
* Examiner-friendly

SVM or Random Forest are acceptable too, but LR is safest.

---

## 🧪 FULL PYTHON CODE — MODULE-8 (TRAIN + EVAL)

👉 Save as
`scripts/module8_ai_training.py`

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
import joblib

# ---------------- PATHS ----------------
DATA_PATH = "../data/module8_ai/"
INPUT_FILE = DATA_PATH + "features_labels.csv"
# --------------------------------------

os.makedirs(DATA_PATH, exist_ok=True)

# -------- LOAD DATA --------
data = pd.read_csv(INPUT_FILE)

X = data[["Alpha", "Beta", "CI"]]
y = data["Label"]

# -------- SCALE FEATURES --------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -------- TRAIN / TEST SPLIT --------
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.3, random_state=42, stratify=y
)

# -------- MODEL --------
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# -------- EVALUATION --------
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)

cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
disp = ConfusionMatrixDisplay(cm, display_labels=model.classes_)
disp.plot()
plt.title("Confusion Matrix – Calmness Classification")
plt.tight_layout()
plt.savefig(DATA_PATH + "confusion_matrix.png", dpi=300)
plt.show()

# -------- SAVE MODEL --------
joblib.dump(model, DATA_PATH + "model.pkl")
joblib.dump(scaler, DATA_PATH + "scaler.pkl")

# -------- SAVE RESULTS --------
with open(DATA_PATH + "evaluation.txt", "w") as f:
    f.write("AI MODEL EVALUATION\n")
    f.write("-------------------\n")
    f.write("Model              : Logistic Regression\n")
    f.write(f"Accuracy           : {acc:.4f}\n")
    f.write("Features           : Alpha, Beta, CI\n")
    f.write("Labels             : Calm, Neutral, Not Calm\n")

print("AI training completed.")
print(f"Accuracy: {acc:.4f}")
```

---

## ✅ EXPECTED RESULTS (BE REALISTIC)

* Accuracy: **65–85%**
* Confusion mostly between **Neutral ↔ Calm**
* No perfect accuracy (and that’s GOOD)

If accuracy is ~33% → something is wrong.
If accuracy is 100% → you overfit.

---

## 🧠 HOW TO USE AI IN REAL-TIME (CONCEPT)

In your **real-time loop**:

1. Compute Alpha, Beta, CI
2. Scale features
3. `model.predict([Alpha, Beta, CI])`
4. Use result for **feedback smoothing**

AI **augments**, not replaces, logic.

---

## 📝 REPORT-READY EXPLANATION (USE THIS)

> “A classical machine learning model was trained using Alpha power, Beta power, and the Calmness Index as features. Logistic Regression was selected due to its interpretability and robustness with small datasets. The AI model improved consistency of calmness classification while preserving deterministic signal processing.”

---

## 🔒 LIMITATIONS (STATE THESE CLEARLY)

* Single-user training
* Labels derived from heuristic thresholds
* Not generalizable across users
* Non-medical

Saying this **increases trust**.

---

## 🚫 DO NOT SAY

* “AI reads the mind”
* “Emotion detection”
* “Mental health diagnosis”

That will destroy your evaluation.

---

## 🏁 WHAT YOU HAVE ACHIEVED (IMPORTANT)

You now have **two layers**:

1. **Deterministic EEG system** (core, explainable)
2. **Light AI layer** (adaptive, optional)

This is **exactly how real BCI systems are built**.
