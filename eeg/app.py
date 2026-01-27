#!/usr/bin/env python3
"""
EEG Calmness Monitor - Complete Web Application
Combines calibration, training, and real-time prediction
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import serial
import serial.tools.list_ports
import numpy as np
import pandas as pd
import time
import os
import joblib
import threading
from collections import deque
from scipy.signal import butter, filtfilt, iirnotch, welch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eeg-monitor-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# ==================== GLOBAL SETTINGS ====================
FS = 250                    # Sampling rate (Hz)
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

# Paths
DATA_DIR = "data"
CALIBRATION_DIR = os.path.join(DATA_DIR, "calibration")
PIPELINE_DIR = os.path.join(DATA_DIR, "pipeline_output")
MODEL_DIR = os.path.join(DATA_DIR, "models")
RESULTS_DIR = os.path.join(DATA_DIR, "results")

for directory in [DATA_DIR, CALIBRATION_DIR, PIPELINE_DIR, MODEL_DIR, RESULTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# ==================== GLOBAL STATE ====================
class AppState:
    def __init__(self):
        self.serial_port = None
        self.is_recording = False
        self.is_predicting = False
        self.recording_mode = None  # 'calm' or 'not_calm'
        self.buffer = deque(maxlen=int(FS * 10))  # 10 second buffer
        self.recording_data = []
        self.model = None
        self.scaler = None
        self.prediction_buffer = deque(maxlen=int(WINDOW_SEC * FS))
        self.last_step_index = 0
        
state = AppState()

# ==================== FILTER FUNCTIONS ====================
def bandpass(data):
    """Apply bandpass filter"""
    nyq = 0.5 * FS
    b, a = butter(4, [LOWCUT/nyq, HIGHCUT/nyq], btype="band")
    return filtfilt(b, a, data)

def notch_filter(data):
    """Apply notch filter"""
    nyq = 0.5 * FS
    b, a = iirnotch(NOTCH/nyq, Q)
    return filtfilt(b, a, data)

def band_power(freqs, psd, band):
    """Calculate power in frequency band"""
    idx = np.logical_and(freqs >= band[0], freqs <= band[1])
    return np.trapz(psd[idx], freqs[idx])

# ==================== PROCESSING FUNCTIONS ====================
def process_calibration_file(filename, label):
    """Process a calibration file through the pipeline"""
    print(f"Processing: {filename}")
    
    # Load raw data
    df = pd.read_csv(os.path.join(CALIBRATION_DIR, filename))
    adc = df["ADC"].values
    time_vals = df["Time(s)"].values
    
    # Convert ADC to voltage
    voltage = (adc / ADC_MAX) * VREF
    
    # Filtering
    filtered = notch_filter(bandpass(voltage))
    
    # Save filtered EEG
    filtered_df = pd.DataFrame({
        "Time(s)": time_vals,
        "Filtered_Voltage": filtered
    })
    filtered_df.to_csv(
        os.path.join(PIPELINE_DIR, f"{label}_filtered.csv"),
        index=False
    )
    
    # Sliding window feature extraction
    window_size = int(WINDOW_SEC * FS)
    step_size = int(STEP_SEC * FS)
    
    # Calculate appropriate nperseg (must be <= window_size)
    nperseg = min(256, window_size)
    
    features = []
    window_id = 1
    
    for start in range(0, len(filtered) - window_size, step_size):
        window = filtered[start:start + window_size]
        
        freqs, psd = welch(window, FS, nperseg=nperseg)
        
        alpha = band_power(freqs, psd, ALPHA_BAND)
        beta = band_power(freqs, psd, BETA_BAND)
        
        if beta == 0:
            continue
        
        ratio = alpha / beta
        
        features.append([window_id, alpha, beta, ratio])
        window_id += 1
    
    # Save features
    feature_df = pd.DataFrame(
        features,
        columns=["Window", "Alpha", "Beta", "AlphaBetaRatio"]
    )
    
    feature_df.to_csv(
        os.path.join(PIPELINE_DIR, f"{label}_features.csv"),
        index=False
    )
    
    return len(feature_df)

def train_model():
    """Train the ML model on calibration data"""
    # Check if feature files exist
    calm_path = os.path.join(PIPELINE_DIR, "calm_features.csv")
    not_calm_path = os.path.join(PIPELINE_DIR, "not_calm_features.csv")
    
    if not os.path.exists(calm_path) or not os.path.exists(not_calm_path):
        return False, "Missing calibration data. Please collect both calm and not calm sessions first."
    
    # Load features
    calm = pd.read_csv(calm_path)
    not_calm = pd.read_csv(not_calm_path)
    
    # Add labels
    calm["Label"] = "Calm"
    not_calm["Label"] = "Not Calm"
    
    # Combine and shuffle
    data = pd.concat([calm, not_calm], ignore_index=True)
    data = data.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Features and labels
    X = data[["Alpha", "Beta", "AlphaBetaRatio"]].values
    y = data["Label"].values
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.3, random_state=42, stratify=y
    )
    
    # Train model
    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = (y_pred == y_test).mean()
    
    # Save model and scaler
    joblib.dump(model, os.path.join(MODEL_DIR, "model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
    
    # Save training report
    report = classification_report(y_test, y_pred)
    with open(os.path.join(MODEL_DIR, "training_report.txt"), "w") as f:
        f.write("EEG CALMNESS MODEL TRAINING REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Samples: {len(data)}\n")
        f.write(f"Calm Samples: {len(calm)}\n")
        f.write(f"Not Calm Samples: {len(not_calm)}\n")
        f.write(f"Test Accuracy: {accuracy:.2%}\n\n")
        f.write("Classification Report:\n")
        f.write(report)
    
    return True, f"Model trained successfully! Accuracy: {accuracy:.2%}"

def serial_reader_thread():
    """Background thread to read serial data"""
    samples_received = 0
    last_print_time = time.time()
    
    while True:
        try:
            if state.serial_port and state.serial_port.is_open:
                try:
                    if state.serial_port.in_waiting:
                        raw = state.serial_port.readline().decode(errors="ignore").strip()
                        if raw.isdigit():
                            adc_value = int(raw)
                            voltage = (adc_value / ADC_MAX) * VREF
                            
                            state.buffer.append(voltage)
                            
                            # If recording, save data
                            if state.is_recording:
                                t = time.time() - state.recording_start_time
                                state.recording_data.append([t, adc_value])
                                
                                # Emit raw waveform data
                                socketio.emit('waveform_data', {
                                    'time': t,
                                    'voltage': voltage,
                                    'mode': 'recording'
                                })
                            
                            # If predicting, process windows
                            elif state.is_predicting and state.model:
                                state.prediction_buffer.append(voltage)
                                samples_received += 1
                                
                                # Print status every second
                                if time.time() - last_print_time >= 1.0:
                                    print(f"Samples/sec: {samples_received}, Buffer: {len(state.prediction_buffer)}/500")
                                    samples_received = 0
                                    last_print_time = time.time()
                                
                                # Emit raw waveform
                                socketio.emit('waveform_data', {
                                    'time': time.time() - state.prediction_start_time,
                                    'voltage': voltage,
                                    'mode': 'prediction'
                                })
                                
                                # Process window
                                process_prediction_window()
                                
                except Exception as e:
                    if state.serial_port:  # Only print if we expect a connection
                        print(f"Serial read error: {e}")
            
            time.sleep(0.001)  # Small delay to prevent CPU hogging
            
        except Exception as e:
            # Catch any outer exceptions to keep thread alive
            time.sleep(0.1)

def process_prediction_window():
    """Process a window for prediction"""
    window_size = int(WINDOW_SEC * FS)
    step_size = int(STEP_SEC * FS)
    
    current_buffer_size = len(state.prediction_buffer)
    
    # Debug: Print buffer status periodically
    if current_buffer_size % 50 == 0 and current_buffer_size > 0:
        print(f"Buffer filling: {current_buffer_size}/{window_size} samples ({current_buffer_size/window_size*100:.1f}%)")
    
    if current_buffer_size >= window_size:
        # Check if enough new data has arrived
        current_index = current_buffer_size
        if current_index - state.last_step_index >= step_size:
            state.last_step_index = current_index
            
            # Get window
            window = np.array(list(state.prediction_buffer)[-window_size:])
            
            print(f"\n{'='*60}")
            print(f"Processing window: {len(window)} samples")
            
            # Filter
            try:
                filtered = notch_filter(bandpass(window))
                print(f"Filtered signal range: {filtered.min():.4f} to {filtered.max():.4f}")
                
                # Calculate appropriate nperseg
                nperseg = min(256, len(filtered))
                
                # Extract features
                freqs, psd = welch(filtered, FS, nperseg=nperseg)
                alpha = band_power(freqs, psd, ALPHA_BAND)
                beta = band_power(freqs, psd, BETA_BAND)
                
                print(f"Alpha power: {alpha:.3e}")
                print(f"Beta power: {beta:.3e}")
                
                if beta > 0:
                    ratio = alpha / beta
                    print(f"Alpha/Beta ratio: {ratio:.3f}")
                    
                    # Predict
                    features = np.array([[alpha, beta, ratio]])
                    features_scaled = state.scaler.transform(features)
                    prediction = state.model.predict(features_scaled)[0]
                    probability = state.model.predict_proba(features_scaled)[0]
                    
                    # Get probability for predicted class
                    pred_idx = 0 if prediction == "Calm" else 1
                    confidence = probability[pred_idx]
                    
                    print(f"Prediction: {prediction} (confidence: {confidence:.2%})")
                    print(f"{'='*60}\n")
                    
                    # Emit prediction
                    socketio.emit('prediction_data', {
                        'time': time.time() - state.prediction_start_time,
                        'alpha': float(alpha),
                        'beta': float(beta),
                        'ratio': float(ratio),
                        'state': prediction,
                        'confidence': float(confidence)
                    })
                else:
                    print(f"Warning: Beta power is zero, skipping prediction")
                    print(f"{'='*60}\n")
                    
            except Exception as e:
                print(f"Prediction error: {e}")
                import traceback
                traceback.print_exc()

# ==================== ROUTES ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ports')
def get_ports():
    """Get list of available serial ports"""
    ports = [port.device for port in serial.tools.list_ports.comports()]
    return jsonify({'ports': ports})

@app.route('/api/connect', methods=['POST'])
def connect_port():
    """Connect to serial port"""
    data = request.json
    port = data.get('port')
    
    try:
        if state.serial_port and state.serial_port.is_open:
            state.serial_port.close()
        
        state.serial_port = serial.Serial(port, 115200, timeout=1)
        time.sleep(2)  # Wait for connection to stabilize
        
        return jsonify({'success': True, 'message': f'Connected to {port}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/disconnect', methods=['POST'])
def disconnect_port():
    """Disconnect serial port"""
    try:
        if state.serial_port and state.serial_port.is_open:
            state.serial_port.close()
        state.serial_port = None
        return jsonify({'success': True, 'message': 'Disconnected'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/start_recording', methods=['POST'])
def start_recording():
    """Start recording calibration data"""
    data = request.json
    mode = data.get('mode')  # 'calm' or 'not_calm'
    
    if not state.serial_port or not state.serial_port.is_open:
        return jsonify({'success': False, 'message': 'Not connected to serial port'})
    
    if state.is_recording or state.is_predicting:
        return jsonify({'success': False, 'message': 'Already recording or predicting'})
    
    state.is_recording = True
    state.recording_mode = mode
    state.recording_data = []
    state.recording_start_time = time.time()
    
    return jsonify({'success': True, 'message': f'Recording {mode} session started'})

@app.route('/api/stop_recording', methods=['POST'])
def stop_recording():
    """Stop recording and save data"""
    if not state.is_recording:
        return jsonify({'success': False, 'message': 'Not currently recording'})
    
    state.is_recording = False
    
    # Save data
    filename = f"{state.recording_mode}_raw.csv"
    filepath = os.path.join(CALIBRATION_DIR, filename)
    
    df = pd.DataFrame(state.recording_data, columns=["Time(s)", "ADC"])
    df.to_csv(filepath, index=False)
    
    # Process through pipeline
    try:
        num_windows = process_calibration_file(filename, state.recording_mode)
        return jsonify({
            'success': True,
            'message': f'Saved {len(state.recording_data)} samples, extracted {num_windows} windows',
            'filename': filename
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing data: {str(e)}'})

@app.route('/api/train_model', methods=['POST'])
def train_model_route():
    """Train the ML model"""
    try:
        success, message = train_model()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Training error: {str(e)}'})

@app.route('/api/start_prediction', methods=['POST'])
def start_prediction():
    """Start real-time prediction"""
    if not state.serial_port or not state.serial_port.is_open:
        return jsonify({'success': False, 'message': 'Not connected to serial port'})
    
    if state.is_recording or state.is_predicting:
        return jsonify({'success': False, 'message': 'Already recording or predicting'})
    
    # Load model
    model_path = os.path.join(MODEL_DIR, "model.pkl")
    scaler_path = os.path.join(MODEL_DIR, "scaler.pkl")
    
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        return jsonify({'success': False, 'message': 'Model not trained yet. Please train model first.'})
    
    try:
        state.model = joblib.load(model_path)
        state.scaler = joblib.load(scaler_path)
        state.is_predicting = True
        state.prediction_buffer.clear()
        state.last_step_index = 0
        state.prediction_start_time = time.time()
        
        print("\n" + "="*60)
        print("PREDICTION MODE STARTED")
        print("="*60)
        print(f"Model loaded: {model_path}")
        print(f"Waiting for {WINDOW_SEC} seconds of data before first prediction...")
        print("Predictions will update every 0.5 seconds after initial window is filled.")
        print("="*60 + "\n")
        
        return jsonify({'success': True, 'message': 'Prediction started - collecting data for first window (2 seconds)...'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error loading model: {str(e)}'})

@app.route('/api/stop_prediction', methods=['POST'])
def stop_prediction():
    """Stop real-time prediction"""
    if not state.is_predicting:
        return jsonify({'success': False, 'message': 'Not currently predicting'})
    
    state.is_predicting = False
    state.model = None
    state.scaler = None
    
    return jsonify({'success': True, 'message': 'Prediction stopped'})

@app.route('/api/status')
def get_status():
    """Get current application status"""
    return jsonify({
        'connected': state.serial_port is not None and state.serial_port.is_open,
        'port': state.serial_port.port if state.serial_port else None,
        'recording': state.is_recording,
        'recording_mode': state.recording_mode,
        'predicting': state.is_predicting,
        'has_model': os.path.exists(os.path.join(MODEL_DIR, "model.pkl")),
        'has_calm_data': os.path.exists(os.path.join(CALIBRATION_DIR, "calm_raw.csv")),
        'has_not_calm_data': os.path.exists(os.path.join(CALIBRATION_DIR, "not_calm_raw.csv"))
    })

# ==================== MAIN ====================
if __name__ == '__main__':
    # Start serial reader thread
    reader_thread = threading.Thread(target=serial_reader_thread, daemon=True)
    reader_thread.start()
    
    print("\n" + "="*60)
    print("EEG CALMNESS MONITOR - Web Application")
    print("="*60)
    print("\nOpen your browser and navigate to: http://localhost:5000")
    print("\nPress CTRL+C to stop the server\n")
    
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)