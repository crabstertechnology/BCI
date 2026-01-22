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
