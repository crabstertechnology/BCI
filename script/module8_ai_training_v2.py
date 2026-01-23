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
