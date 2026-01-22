import csv
import os

BANDPOWER_FILE = "../data/module6_bandpower_extraction/bandpower_windows.csv"
CALMNESS_FILE  = "../data/module7_calmness_final/calmness_timeline.csv"
OUT_PATH = "../data/module8_ai/"
OUT_FILE = OUT_PATH + "features_labels.csv"

os.makedirs(OUT_PATH, exist_ok=True)

# Load bandpower
bandpower = {}
with open(BANDPOWER_FILE, "r") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        bandpower[int(row[0])] = {
            "alpha": float(row[1]),
            "beta": float(row[2])
        }

# Load calmness + labels
rows = []
with open(CALMNESS_FILE, "r") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        window = int(row[0])
        ci = float(row[3])
        label = row[4]

        if window in bandpower:
            rows.append([
                bandpower[window]["alpha"],
                bandpower[window]["beta"],
                ci,
                label
            ])

# Save AI input CSV
with open(OUT_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Alpha", "Beta", "CI", "Label"])
    writer.writerows(rows)

print("features_labels.csv created successfully.")
