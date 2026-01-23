import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

# ---------------- PATHS ----------------
DATA_PATH = "../data/module8_ai/"
INPUT_FILE = DATA_PATH + "features_labels_v3.csv"
# --------------------------------------

# -------- LOAD DATA --------
df = pd.read_csv(INPUT_FILE)

print("\nLabel distribution:")
print(df["Label"].value_counts())

# -------- FEATURES & LABELS --------
X = df[["Alpha", "Beta", "AlphaBetaRatio"]]
y = df["Label"]

# -------- SCALE FEATURES --------
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
disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=model.classes_
)
disp.plot()
plt.title("Confusion Matrix – Final Calmness Model")
plt.tight_layout()
plt.savefig(DATA_PATH + "confusion_matrix_final.png", dpi=300)
plt.show()

# -------- SAVE MODEL --------
joblib.dump(model, DATA_PATH + "model_final.pkl")
joblib.dump(scaler, DATA_PATH + "scaler_final.pkl")

# -------- SAVE TRAINING REPORT --------
with open(DATA_PATH + "training_report_final.txt", "w") as f:
    f.write("FINAL AI TRAINING REPORT\n")
    f.write("------------------------\n")
    f.write("Model           : Logistic Regression\n")
    f.write("Classes         : Calm, Not Calm\n")
    f.write("Features        : Alpha, Beta, AlphaBetaRatio\n")
    f.write("Labeling        : Session-level calibration\n")
    f.write("Class balancing : Enabled\n")

print("\nFinal model training completed.")
