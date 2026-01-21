import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
import csv
import os

# ---------------- SETTINGS ----------------
FS = 250
ALPHA_BAND = (8, 13)
BETA_BAND = (13, 30)

DATA_PATH = "../data/module4_alpha_beta_comparison/"
OPEN_FILE = DATA_PATH + "eyes_open_filtered.csv"
CLOSED_FILE = DATA_PATH + "eyes_closed_filtered.csv"
# ------------------------------------------

def load_signal(filename):
    signal = []
    with open(filename, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            signal.append(float(row[1]))
    return np.array(signal)

def band_power(freqs, psd, band):
    idx = np.logical_and(freqs >= band[0], freqs <= band[1])
    return np.trapz(psd[idx], freqs[idx])

# -------- LOAD DATA --------
eeg_open = load_signal(OPEN_FILE)
eeg_closed = load_signal(CLOSED_FILE)

# -------- PSD --------
f_open, psd_open = welch(eeg_open, FS, nperseg=1024)
f_closed, psd_closed = welch(eeg_closed, FS, nperseg=1024)

# -------- BAND POWER --------
alpha_open = band_power(f_open, psd_open, ALPHA_BAND)
beta_open = band_power(f_open, psd_open, BETA_BAND)

alpha_closed = band_power(f_closed, psd_closed, ALPHA_BAND)
beta_closed = band_power(f_closed, psd_closed, BETA_BAND)

ratio_open = alpha_open / beta_open if beta_open != 0 else 0
ratio_closed = alpha_closed / beta_closed if beta_closed != 0 else 0

# -------- PSD COMPARISON PLOT --------
plt.figure(figsize=(10,5))
plt.semilogy(f_open, psd_open, label="Eyes Open")
plt.semilogy(f_closed, psd_closed, label="Eyes Closed")
plt.axvspan(8, 13, color='green', alpha=0.2, label="Alpha Band")
plt.axvspan(13, 30, color='red', alpha=0.2, label="Beta Band")
plt.xlim(0, 40)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Power")
plt.title("PSD Comparison: Eyes Open vs Eyes Closed")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(DATA_PATH + "psd_comparison.png", dpi=300)
plt.show()

# -------- BAR COMPARISON --------
labels = ["Alpha Open", "Alpha Closed", "Beta Open", "Beta Closed"]
values = [alpha_open, alpha_closed, beta_open, beta_closed]

plt.figure(figsize=(7,4))
plt.bar(labels, values)
plt.ylabel("Power")
plt.title("Alpha & Beta Band Power Comparison")
plt.tight_layout()
plt.savefig(DATA_PATH + "bandpower_comparison.png", dpi=300)
plt.show()

# -------- SAVE STATS --------
with open(DATA_PATH + "comparison_stats.txt", "w") as f:
    f.write("MODULE-4: ALPHA/BETA COMPARISON\n")
    f.write("--------------------------------\n")
    f.write(f"Alpha Power (Eyes Open)   : {alpha_open:.6e}\n")
    f.write(f"Alpha Power (Eyes Closed) : {alpha_closed:.6e}\n")
    f.write(f"Beta Power (Eyes Open)    : {beta_open:.6e}\n")
    f.write(f"Beta Power (Eyes Closed)  : {beta_closed:.6e}\n")
    f.write(f"Alpha/Beta (Eyes Open)   : {ratio_open:.4f}\n")
    f.write(f"Alpha/Beta (Eyes Closed) : {ratio_closed:.4f}\n")

print("Module-4 Alpha/Beta comparison completed.")
print(f"Alpha/Beta (Open)   : {ratio_open:.4f}")
print(f"Alpha/Beta (Closed) : {ratio_closed:.4f}")
