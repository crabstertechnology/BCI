import serial
import numpy as np
import matplotlib.pyplot as plt
import time
import csv
import os

# ---------------- USER SETTINGS ----------------
PORT = 'COM6'          # 🔴 Change this
BAUD_RATE = 115200
ADC_MAX = 4095         # UNO R4 = 12-bit
VREF = 3.3
FS = 250               # Sampling rate
DURATION = 60          # seconds
SAVE_PATH = "../data/test1_baseline/"
# ------------------------------------------------

os.makedirs(SAVE_PATH, exist_ok=True)

ser = serial.Serial(PORT, BAUD_RATE)
time.sleep(2)

samples = FS * DURATION
eeg = []
timestamps = []

print("TEST-1: Baseline Stability Test")
print("Sit still, eyes open, breathe normally...")

start_time = time.time()

while len(eeg) < samples:
    if ser.in_waiting:
        raw = ser.readline().decode(errors='ignore').strip()
        if raw.isdigit():
            adc = int(raw)
            voltage = (adc / ADC_MAX) * VREF
            eeg.append(voltage)
            timestamps.append(time.time() - start_time)

ser.close()

eeg = np.array(eeg)
timestamps = np.array(timestamps)

# ---------------- SAVE RAW DATA ----------------
csv_file = SAVE_PATH + "raw_data.csv"
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Time (s)", "Voltage (V)"])
    for t, v in zip(timestamps, eeg):
        writer.writerow([t, v])

# ---------------- PLOT ----------------
plt.figure(figsize=(12,4))
plt.plot(timestamps, eeg, linewidth=0.8)
plt.title("Baseline EEG Signal (Eyes Open)")
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.grid(True)
plt.tight_layout()

plot_file = SAVE_PATH + "baseline_plot.png"
plt.savefig(plot_file, dpi=300)
plt.show()

# ---------------- STATISTICS ----------------
mean_v = np.mean(eeg)
std_v = np.std(eeg)
min_v = np.min(eeg)
max_v = np.max(eeg)

stats_file = SAVE_PATH + "stats.txt"
with open(stats_file, "w") as f:
    f.write("TEST-1: BASELINE STABILITY RESULTS\n")
    f.write("--------------------------------\n")
    f.write(f"Duration        : {DURATION} seconds\n")
    f.write(f"Sampling Rate   : {FS} Hz\n")
    f.write(f"Mean Voltage    : {mean_v:.6f} V\n")
    f.write(f"Std Deviation   : {std_v:.6f} V\n")
    f.write(f"Min Voltage     : {min_v:.6f} V\n")
    f.write(f"Max Voltage     : {max_v:.6f} V\n")

print("\nTest completed.")
print(f"Data saved to: {SAVE_PATH}")
print(f"Std Deviation: {std_v:.6f} V")
