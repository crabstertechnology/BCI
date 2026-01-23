import serial
import numpy as np
import time
import csv
import os
import joblib
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, iirnotch, welch

# ================= SETTINGS =================
PORT = "COM6"              # 🔴 change if needed
BAUD = 115200

FS = 250
ADC_MAX = 4095
VREF = 3.3

WINDOW_SEC = 2.0
STEP_SEC = 0.5

LOWCUT = 0.5
HIGHCUT = 40
NOTCH = 50
Q = 30

MODEL_PATH = "../data/module8_ai/model_final.pkl"
SCALER_PATH = "../data/module8_ai/scaler_final.pkl"

SAVE_PATH = "../data/module9_realtime_ai/"
LOG_FILE = SAVE_PATH + "realtime_ai_log_final.csv"
# ===========================================

os.makedirs(SAVE_PATH, exist_ok=True)

# -------- LOAD MODEL --------
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# -------- FILTER FUNCTIONS --------
def bandpass(data):
    nyq = 0.5 * FS
    b, a = butter(4, [LOWCUT/nyq, HIGHCUT/nyq], btype="band")
    return filtfilt(b, a, data)

def notch(data):
    nyq = 0.5 * FS
    b, a = iirnotch(NOTCH/nyq, Q)
    return filtfilt(b, a, data)

def band_power(freqs, psd, band):
    idx = np.logical_and(freqs >= band[0], freqs <= band[1])
    return np.trapz(psd[idx], freqs[idx])

# -------- SERIAL --------
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

buffer = []
window_samples = int(WINDOW_SEC * FS)
step_samples = int(STEP_SEC * FS)

# -------- CSV LOG --------
log = open(LOG_FILE, "w", newline="")
writer = csv.writer(log)
writer.writerow([
    "Time(s)",
    "Alpha",
    "Beta",
    "AlphaBetaRatio",
    "AI_State"
])

# -------- LIVE PLOT --------
plt.ion()
fig, ax = plt.subplots()
ratio_vals = []
line, = ax.plot([], [], marker="o")
ax.set_ylim(0, 3)
ax.set_title("Real-Time Calmness Prediction (Final)")
ax.set_xlabel("Window")
ax.set_ylabel("Alpha / Beta Ratio")
ax.grid(True)

t0 = time.time()

print("Real-time prediction started (CTRL+C to stop)")

try:
    while True:
        # ---- READ SERIAL ----
        if ser.in_waiting:
            raw = ser.readline().decode(errors="ignore").strip()
            if raw.isdigit():
                voltage = (int(raw) / ADC_MAX) * VREF
                buffer.append(voltage)

        # ---- PROCESS WINDOW ----
        if len(buffer) >= window_samples:
            window = np.array(buffer[:window_samples])
            buffer = buffer[step_samples:]

            filt = notch(bandpass(window))

            freqs, psd = welch(filt, FS, nperseg=512)

            alpha = band_power(freqs, psd, (8, 13))
            beta  = band_power(freqs, psd, (13, 30))

            if beta == 0:
                continue

            ratio = alpha / beta

            features = np.array([[alpha, beta, ratio]])
            features_scaled = scaler.transform(features)
            state = model.predict(features_scaled)[0]

            t = time.time() - t0

            writer.writerow([
                f"{t:.2f}",
                alpha,
                beta,
                ratio,
                state
            ])

            ratio_vals.append(ratio)
            line.set_data(range(len(ratio_vals)), ratio_vals)
            ax.set_xlim(0, len(ratio_vals))
            plt.pause(0.01)

            print(f"[{t:6.1f}s] A/B={ratio:.2f} → {state}")

except KeyboardInterrupt:
    print("\nStopping real-time prediction...")

finally:
    ser.close()
    log.close()
    plt.ioff()
    plt.show()
    print(f"Saved log to: {LOG_FILE}")
