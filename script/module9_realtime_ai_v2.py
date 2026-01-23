import serial
import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, iirnotch, welch
import joblib
import csv
import os

# ---------------- SETTINGS ----------------
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

MODEL_PATH = "../data/module8_ai/model_v2.pkl"
SCALER_PATH = "../data/module8_ai/scaler_v2.pkl"

SAVE_PATH = "../data/module9_realtime_ai/"
LOG_FILE = SAVE_PATH + "realtime_ai_log_v2.csv"
# -----------------------------------------

os.makedirs(SAVE_PATH, exist_ok=True)

# -------- LOAD AI MODEL --------
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# -------- FILTER FUNCTIONS --------
def bandpass(data):
    nyq = 0.5 * FS
    b, a = butter(4, [LOWCUT / nyq, HIGHCUT / nyq], btype="band")
    return filtfilt(b, a, data)

def notch(data):
    nyq = 0.5 * FS
    b, a = iirnotch(NOTCH / nyq, Q)
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
ratio_values = []
line, = ax.plot([], [], marker="o")

ax.set_ylim(0, 3)
ax.set_title("Real-Time Calmness Detection (AI v2)")
ax.set_xlabel("Window")
ax.set_ylabel("Alpha / Beta Ratio")
ax.grid(True)

t0 = time.time()

print("Real-time AI detection started (CTRL+C to stop).")

try:
    while True:
        # -------- READ SERIAL --------
        if ser.in_waiting:
            raw = ser.readline().decode(errors="ignore").strip()
            if raw.isdigit():
                adc = int(raw)
                voltage = (adc / ADC_MAX) * VREF
                buffer.append(voltage)

        # -------- PROCESS WINDOW --------
        if len(buffer) >= window_samples:
            window = np.array(buffer[:window_samples])
            buffer = buffer[step_samples:]

            # Filter EEG
            filt = notch(bandpass(window))

            # FFT
            freqs, psd = welch(filt, FS, nperseg=512)

            alpha = band_power(freqs, psd, (8, 13))
            beta  = band_power(freqs, psd, (13, 30))

            if beta == 0:
                continue

            alpha_beta_ratio = alpha / beta

            # -------- AI PREDICTION --------
            features = np.array([[alpha, beta, alpha_beta_ratio]])
            features_scaled = scaler.transform(features)
            state = model.predict(features_scaled)[0]

            # -------- TIME --------
            t = time.time() - t0

            # -------- LOG --------
            writer.writerow([
                f"{t:.2f}",
                alpha,
                beta,
                alpha_beta_ratio,
                state
            ])

            # -------- PLOT --------
            ratio_values.append(alpha_beta_ratio)
            line.set_data(range(len(ratio_values)), ratio_values)
            ax.set_xlim(0, len(ratio_values))
            plt.pause(0.01)

            print(f"[{t:6.1f}s] A/B={alpha_beta_ratio:.2f} → {state}")

except KeyboardInterrupt:
    print("\nStopping real-time AI detection...")

finally:
    ser.close()
    log.close()
    plt.ioff()
    plt.show()
    print(f"Data saved to: {LOG_FILE}")
