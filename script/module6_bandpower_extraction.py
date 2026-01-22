import numpy as np
import csv
import os
import matplotlib.pyplot as plt
from scipy.signal import welch

# ---------------- SETTINGS ----------------
FS = 250                     # Sampling rate (Hz)
WINDOW_SEC = 2.0             # Window length (seconds)
STEP_SEC = 0.5               # Step size (seconds)

ALPHA_BAND = (8, 13)
BETA_BAND  = (13, 30)

DATA_PATH = "../data/module6_bandpower_extraction/"
INPUT_FILE = DATA_PATH + "filtered_input.csv"
# ------------------------------------------

os.makedirs(DATA_PATH, exist_ok=True)

# -------- LOAD FILTERED EEG --------
signal = []

with open(INPUT_FILE, "r") as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        signal.append(float(row[1]))

signal = np.array(signal)

# -------- SLIDING WINDOW PARAMETERS --------
window_size = int(WINDOW_SEC * FS)
step_size = int(STEP_SEC * FS)

def band_power(freqs, psd, band):
    idx = np.logical_and(freqs >= band[0], freqs <= band[1])
    return np.trapz(psd[idx], freqs[idx])

# -------- SLIDING WINDOW FFT --------
alpha_list = []
beta_list = []
window_index = []

win = 1
for start in range(0, len(signal) - window_size, step_size):
    window = signal[start:start + window_size]

    freqs, psd = welch(window, fs=FS, nperseg=256)

    alpha = band_power(freqs, psd, ALPHA_BAND)
    beta  = band_power(freqs, psd, BETA_BAND)

    alpha_list.append(alpha)
    beta_list.append(beta)
    window_index.append(win)
    win += 1

alpha_arr = np.array(alpha_list)
beta_arr = np.array(beta_list)

# -------- SAVE BANDPOWER CSV --------
csv_file = DATA_PATH + "bandpower_windows.csv"
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Window", "Alpha_Power", "Beta_Power"])
    for i, a, b in zip(window_index, alpha_arr, beta_arr):
        writer.writerow([i, a, b])

# -------- PLOT FOR VERIFICATION --------
plt.figure(figsize=(10,4))
plt.plot(alpha_arr, label="Alpha Power")
plt.plot(beta_arr, label="Beta Power")
plt.xlabel("Window Index")
plt.ylabel("Power")
plt.title("Alpha and Beta Band Power (Sliding Windows)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(DATA_PATH + "alpha_beta_plot.png", dpi=300)
plt.show()

# -------- SAVE EXTRACTION INFO --------
with open(DATA_PATH + "extraction_info.txt", "w") as f:
    f.write("SLIDING WINDOW BAND POWER EXTRACTION\n")
    f.write("-----------------------------------\n")
    f.write(f"Sampling Rate      : {FS} Hz\n")
    f.write(f"Window Length      : {WINDOW_SEC} s\n")
    f.write(f"Step Size          : {STEP_SEC} s\n")
    f.write(f"Alpha Band         : {ALPHA_BAND[0]}–{ALPHA_BAND[1]} Hz\n")
    f.write(f"Beta Band          : {BETA_BAND[0]}–{BETA_BAND[1]} Hz\n")
    f.write(f"Total Windows      : {len(alpha_arr)}\n")

print("Band power extraction completed.")
print(f"Saved to: {DATA_PATH}")
