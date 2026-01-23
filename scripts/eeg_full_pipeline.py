import numpy as np
import pandas as pd
import os
from scipy.signal import butter, filtfilt, iirnotch, welch

# ================= SETTINGS =================
FS = 250                     # Sampling rate (Hz)
ADC_MAX = 4095
VREF = 3.3

LOWCUT = 0.5
HIGHCUT = 40
NOTCH = 50
Q = 30

WINDOW_SEC = 2.0
STEP_SEC = 0.5

ALPHA_BAND = (8, 13)
BETA_BAND = (13, 30)

INPUT_PATH = "../data/calibration/"
OUTPUT_PATH = "../data/pipeline_output/"
# ===========================================

os.makedirs(OUTPUT_PATH, exist_ok=True)

# ---------- FILTER FUNCTIONS ----------
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

# ---------- CORE PIPELINE FUNCTION ----------
def process_file(filename, label):
    print(f"\nProcessing: {filename}")

    # Load raw data
    df = pd.read_csv(INPUT_PATH + filename)
    adc = df["ADC"].values
    time_vals = df["Time(s)"].values

    # Convert ADC to voltage
    voltage = (adc / ADC_MAX) * VREF

    # Filtering
    filtered = notch(bandpass(voltage))

    # Save filtered EEG
    filtered_df = pd.DataFrame({
        "Time(s)": time_vals,
        "Filtered_Voltage": filtered
    })
    filtered_df.to_csv(
        OUTPUT_PATH + f"{label}_filtered.csv",
        index=False
    )

    # Sliding window parameters
    window_size = int(WINDOW_SEC * FS)
    step_size = int(STEP_SEC * FS)

    features = []
    window_id = 1

    for start in range(0, len(filtered) - window_size, step_size):
        window = filtered[start:start + window_size]

        freqs, psd = welch(window, FS, nperseg=512)

        alpha = band_power(freqs, psd, ALPHA_BAND)
        beta = band_power(freqs, psd, BETA_BAND)

        if beta == 0:
            continue

        ratio = alpha / beta

        features.append([
            window_id,
            alpha,
            beta,
            ratio
        ])

        window_id += 1

    # Save features
    feature_df = pd.DataFrame(
        features,
        columns=["Window", "Alpha", "Beta", "AlphaBetaRatio"]
    )

    feature_df.to_csv(
        OUTPUT_PATH + f"{label}_features.csv",
        index=False
    )

    print(f"Saved {label}_features.csv ({len(feature_df)} windows)")

# ---------- RUN PIPELINE ----------
process_file("calm_raw.csv", "calm")
process_file("not_calm_raw.csv", "not_calm")

print("\nPipeline completed successfully.")
