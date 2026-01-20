import serial
import numpy as np
import matplotlib.pyplot as plt
import time
import csv
import os

# ---------------- USER SETTINGS ----------------
PORT = 'COM6'          # 🔴 Change this
BAUD_RATE = 115200
ADC_MAX = 4095
VREF = 3.3
FS = 250
DURATION = 20          # seconds per condition
SAVE_PATH = "../data/test3_eyes_open_closed/"
# ------------------------------------------------

os.makedirs(SAVE_PATH, exist_ok=True)

def record_eeg(label):
    ser = serial.Serial(PORT, BAUD_RATE)
    time.sleep(2)

    eeg = []
    timestamps = []

    print(f"Recording: {label}")
    start_time = time.time()

    while len(eeg) < FS * DURATION:
        if ser.in_waiting:
            raw = ser.readline().decode(errors="ignore").strip()
            if raw.isdigit():
                adc = int(raw)
                voltage = (adc / ADC_MAX) * VREF
                eeg.append(voltage)
                timestamps.append(time.time() - start_time)

    ser.close()
    return np.array(timestamps), np.array(eeg)

# -------- RECORD EYES OPEN --------
input("Press ENTER and keep EYES OPEN...")
t_open, eeg_open = record_eeg("Eyes Open")

# -------- SHORT PAUSE --------
print("Relax for 5 seconds...")
time.sleep(5)

# -------- RECORD EYES CLOSED --------
input("Press ENTER and keep EYES CLOSED...")
t_closed, eeg_closed = record_eeg("Eyes Closed")

# -------- SAVE DATA --------
def save_csv(filename, t, eeg):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Time (s)", "Voltage (V)"])
        for ti, vi in zip(t, eeg):
            writer.writerow([ti, vi])

save_csv(SAVE_PATH + "eyes_open.csv", t_open, eeg_open)
save_csv(SAVE_PATH + "eyes_closed.csv", t_closed, eeg_closed)

# -------- PLOT COMPARISON --------
plt.figure(figsize=(12,6))

plt.subplot(2,1,1)
plt.plot(t_open, eeg_open, linewidth=0.8)
plt.title("Eyes Open – Raw EEG")
plt.ylabel("Voltage (V)")
plt.grid(True)

plt.subplot(2,1,2)
plt.plot(t_closed, eeg_closed, linewidth=0.8)
plt.title("Eyes Closed – Raw EEG")
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.grid(True)

plt.tight_layout()
plt.savefig(SAVE_PATH + "comparison_plot.png", dpi=300)
plt.show()

# -------- BASIC STATS --------
stats_file = SAVE_PATH + "stats.txt"
with open(stats_file, "w") as f:
    f.write("TEST-3: EYES OPEN vs EYES CLOSED\n")
    f.write("--------------------------------\n")
    f.write(f"Eyes Open  - Std Dev : {np.std(eeg_open):.6f} V\n")
    f.write(f"Eyes Closed- Std Dev : {np.std(eeg_closed):.6f} V\n")

print("\nTest-3 completed.")
print("Files saved to:", SAVE_PATH)
