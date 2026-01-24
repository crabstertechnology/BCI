import serial
import threading
import time
import numpy as np
from flask import Flask, render_template, jsonify
import joblib
from scipy.signal import butter, filtfilt, iirnotch, welch

# ================= SETTINGS =================
PORT = "COM6"
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

MODEL_PATH = "model/model_final.pkl"
SCALER_PATH = "model/scaler_final.pkl"
# ===========================================

# -------- LOAD MODEL --------
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# -------- FLASK --------
app = Flask(__name__)

latest_data = {
    "ratio": [],
    "state": "Waiting..."
}

# -------- FILTERS --------
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

# -------- EEG THREAD --------
def eeg_loop():
    global latest_data

    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)

    buffer = []
    window_samples = int(WINDOW_SEC * FS)
    step_samples = int(STEP_SEC * FS)

    while True:
        if ser.in_waiting:
            raw = ser.readline().decode(errors="ignore").strip()
            if raw.isdigit():
                v = (int(raw) / ADC_MAX) * VREF
                buffer.append(v)

        if len(buffer) >= window_samples:
            window = np.array(buffer[:window_samples])
            buffer = buffer[step_samples:]

            filt = notch(bandpass(window))
            freqs, psd = welch(filt, FS, nperseg=512)

            alpha = band_power(freqs, psd, (8, 13))
            beta = band_power(freqs, psd, (13, 30))

            if beta == 0:
                continue

            ratio = alpha / beta
            features = scaler.transform([[alpha, beta, ratio]])
            state = model.predict(features)[0]

            latest_data["ratio"].append(ratio)
            latest_data["ratio"] = latest_data["ratio"][-50:]
            latest_data["state"] = state

# -------- ROUTES --------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/live")
def live_data():
    return jsonify(latest_data)

# -------- START --------
if __name__ == "__main__":
    t = threading.Thread(target=eeg_loop, daemon=True)
    t.start()
    app.run(debug=False)
