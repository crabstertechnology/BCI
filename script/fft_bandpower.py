import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
import csv
import os

# ---------------- SETTINGS ----------------
FS = 250                 # Sampling rate (Hz)
ALPHA_BAND = (8, 13)
BETA_BAND = (13, 30)

DATA_PATH = "../data/module3_fft_bandpower/"
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

# -------- FFT USING WELCH PSD --------
freqs, psd = welch(signal, FS, nperseg=1024)

# -------- BAND POWER FUNCTION --------
def band_power(freqs, psd, band):
    idx = np.logical_and(freqs >= band[0], freqs <= band[1])
    return np.trapz(psd[idx], freqs[idx])

alpha_power = band_power(freqs, psd, ALPHA_BAND)
beta_power = band_power(freqs, psd, BETA_BAND)
alpha_beta_ratio = alpha_power / beta_power if beta_power != 0 else 0

# -------- SAVE RESULTS --------
with open(DATA_PATH + "band_power.txt", "w") as f:
    f.write("MODULE-3: FFT & BAND POWER RESULTS\n")
    f.write("---------------------------------\n")
    f.write(f"Alpha Band (8–13 Hz) Power : {alpha_power:.6e}\n")
    f.write(f"Beta Band (13–30 Hz) Power : {beta_power:.6e}\n")
    f.write(f"Alpha/Beta Ratio          : {alpha_beta_ratio:.4f}\n")

# -------- FFT PLOT --------
plt.figure(figsize=(10,5))
plt.semilogy(freqs, psd)
plt.axvspan(8, 13, color='green', alpha=0.3, label='Alpha Band')
plt.axvspan(13, 30, color='red', alpha=0.3, label='Beta Band')
plt.xlim(0, 40)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Power")
plt.title("EEG Power Spectral Density (FFT)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(DATA_PATH + "fft_plot.png", dpi=300)
plt.show()

# -------- BAR GRAPH --------
plt.figure(figsize=(6,4))
plt.bar(["Alpha Power", "Beta Power"], [alpha_power, beta_power])
plt.ylabel("Power")
plt.title("Alpha vs Beta Band Power")
plt.tight_layout()
plt.savefig(DATA_PATH + "band_power_bar.png", dpi=300)
plt.show()

print("Module-3 FFT & Band Power completed.")
print(f"Alpha Power      : {alpha_power:.6e}")
print(f"Beta Power       : {beta_power:.6e}")
print(f"Alpha/Beta Ratio : {alpha_beta_ratio:.4f}")
