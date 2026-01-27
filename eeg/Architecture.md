# 🏗️ System Architecture - EEG Calmness Monitor

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                    (Web Browser - HTML/CSS/JS)                   │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Connection   │  │ Calibration  │  │  Prediction  │          │
│  │   Panel      │  │    Panel     │  │    Panel     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌────────────────────────────────────────────────────┐         │
│  │          Live Waveform Chart (Chart.js)            │         │
│  └────────────────────────────────────────────────────┘         │
│                                                                   │
│  ┌────────────────────────────────────────────────────┐         │
│  │        Feature Analysis Chart (Chart.js)           │         │
│  └────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK WEB SERVER                            │
│                    (Python Backend - app.py)                     │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ REST API     │  │ SocketIO     │  │ State Mgmt   │          │
│  │ Endpoints    │  │ Real-time    │  │ (AppState)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌────────────────────────────────────────────────────┐         │
│  │         Serial Reader Thread (Background)          │         │
│  │  • Continuous data acquisition from Arduino        │         │
│  │  • Buffering and streaming                         │         │
│  └────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ↕ Serial (115200 baud)
┌─────────────────────────────────────────────────────────────────┐
│                         ARDUINO                                  │
│                  (Hardware Interface)                            │
│                                                                   │
│  ┌────────────────────────────────────────────────────┐         │
│  │  EEG Sensor → ADC (A0) → Serial TX → USB          │         │
│  │  Sampling: 250 Hz (4ms intervals)                  │         │
│  └────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### 1. Calibration Data Collection Flow

```
User Clicks "Record Calm/Not Calm"
              ↓
    Backend starts recording
              ↓
    ┌─────────────────────┐
    │ Serial Reader Thread│
    │ (Continuous Loop)   │
    └─────────────────────┘
              ↓
    Read ADC value from Arduino
              ↓
    Convert ADC → Voltage
              ↓
    Add to recording buffer
              ↓
    Emit to frontend via WebSocket
              ↓
    Update live waveform chart
              ↓
    [User watches live signal]
              ↓
    User clicks "Stop Recording"
              ↓
    Save raw data to CSV
              ↓
    ┌─────────────────────┐
    │ Signal Processing   │
    └─────────────────────┘
              ↓
    Bandpass filter (0.5-40 Hz)
              ↓
    Notch filter (50 Hz)
              ↓
    Save filtered signal
              ↓
    ┌─────────────────────┐
    │ Feature Extraction  │
    └─────────────────────┘
              ↓
    Sliding window (2s, 0.5s step)
              ↓
    For each window:
      • Welch's method → PSD
      • Integrate Alpha band (8-13 Hz)
      • Integrate Beta band (13-30 Hz)
      • Calculate α/β ratio
              ↓
    Save features to CSV
              ↓
    Update status (data available)
```

### 2. Model Training Flow

```
User clicks "Train Model"
              ↓
    Check for both datasets
              ↓
    Load calm_features.csv
    Load not_calm_features.csv
              ↓
    Add labels:
      • Calm → "Calm"
      • Not Calm → "Not Calm"
              ↓
    Combine datasets
              ↓
    Shuffle data (random_state=42)
              ↓
    Extract features:
      X = [Alpha, Beta, AlphaBetaRatio]
      y = Labels
              ↓
    Split data:
      70% training
      30% testing
      (stratified by class)
              ↓
    ┌─────────────────────┐
    │ Feature Scaling     │
    └─────────────────────┘
              ↓
    StandardScaler:
      • Fit on training data
      • Transform train & test
              ↓
    ┌─────────────────────┐
    │ Model Training      │
    └─────────────────────┘
              ↓
    Logistic Regression:
      • max_iter: 1000
      • class_weight: balanced
              ↓
    Fit on training data
              ↓
    ┌─────────────────────┐
    │ Evaluation          │
    └─────────────────────┘
              ↓
    Predict on test data
              ↓
    Calculate metrics:
      • Accuracy
      • Precision
      • Recall
      • F1-Score
              ↓
    Save model.pkl
    Save scaler.pkl
    Save training_report.txt
              ↓
    Return accuracy to user
```

### 3. Real-Time Prediction Flow

```
User clicks "Start Prediction"
              ↓
    Load model.pkl
    Load scaler.pkl
              ↓
    Clear prediction buffer
              ↓
    ┌─────────────────────────────┐
    │ Continuous Prediction Loop  │
    │ (Runs in Serial Thread)     │
    └─────────────────────────────┘
              ↓
    Read ADC from Arduino
              ↓
    Convert ADC → Voltage
              ↓
    Add to prediction buffer
              ↓
    Emit raw voltage to frontend
              ↓
    Update live waveform
              ↓
    Buffer reaches 500 samples (2s)?
              ↓ Yes
    ┌─────────────────────┐
    │ Signal Processing   │
    └─────────────────────┘
              ↓
    Bandpass filter (0.5-40 Hz)
              ↓
    Notch filter (50 Hz)
              ↓
    ┌─────────────────────┐
    │ Feature Extraction  │
    └─────────────────────┘
              ↓
    Welch's method → PSD
              ↓
    Calculate Alpha power
    Calculate Beta power
    Calculate α/β ratio
              ↓
    ┌─────────────────────┐
    │ Classification      │
    └─────────────────────┘
              ↓
    Create feature vector:
      [Alpha, Beta, Ratio]
              ↓
    Scale features using scaler
              ↓
    Predict class using model
              ↓
    Get prediction probability
              ↓
    ┌─────────────────────┐
    │ Display Results     │
    └─────────────────────┘
              ↓
    Emit to frontend:
      • State (Calm/Not Calm)
      • Alpha value
      • Beta value
      • Ratio value
      • Confidence
              ↓
    Update prediction display
    Update metrics panel
    Update feature chart
              ↓
    Slide buffer by 125 samples
              ↓
    [Continue loop]
```

---

## Component Architecture

### Frontend Components (HTML/JS)

```
┌─────────────────────────────────────────────┐
│              index.html                      │
├─────────────────────────────────────────────┤
│                                              │
│  ┌────────────────────────────────────┐    │
│  │ Status Bar Component               │    │
│  │ • Connection indicator             │    │
│  │ • Mode display                     │    │
│  │ • Model status                     │    │
│  │ • Data availability                │    │
│  └────────────────────────────────────┘    │
│                                              │
│  ┌────────────────┐  ┌─────────────────┐   │
│  │ Connection     │  │ Calibration     │   │
│  │ Panel          │  │ Panel           │   │
│  │ • Port select  │  │ • Record calm   │   │
│  │ • Connect btn  │  │ • Record active │   │
│  │ • Disconnect   │  │ • Stop button   │   │
│  └────────────────┘  └─────────────────┘   │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │ Training Panel                     │    │
│  │ • Train button                     │    │
│  │ • Status messages                  │    │
│  └────────────────────────────────────┘    │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │ Prediction Panel                   │    │
│  │ • Start/Stop buttons               │    │
│  │ • State display (large)            │    │
│  │ • Metrics (Alpha/Beta/Ratio)       │    │
│  └────────────────────────────────────┘    │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │ Chart Components                   │    │
│  │ • Waveform Chart (Chart.js)        │    │
│  │ • Feature Chart (Chart.js)         │    │
│  └────────────────────────────────────┘    │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │ JavaScript Controllers             │    │
│  │ • Socket.IO client                 │    │
│  │ • API client functions             │    │
│  │ • Chart initialization             │    │
│  │ • Event handlers                   │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### Backend Components (Python)

```
┌─────────────────────────────────────────────┐
│              app.py                          │
├─────────────────────────────────────────────┤
│                                              │
│  ┌────────────────────────────────────┐    │
│  │ Flask Application                  │    │
│  │ • Route handlers                   │    │
│  │ • SocketIO setup                   │    │
│  │ • Configuration                    │    │
│  └────────────────────────────────────┘    │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │ AppState (Global State Manager)    │    │
│  │ • serial_port                      │    │
│  │ • is_recording                     │    │
│  │ • is_predicting                    │    │
│  │ • buffers (deque)                  │    │
│  │ • model & scaler                   │    │
│  └────────────────────────────────────┘    │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │ Signal Processing Module           │    │
│  │ • bandpass()                       │    │
│  │ • notch_filter()                   │    │
│  │ • band_power()                     │    │
│  └────────────────────────────────────┘    │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │ Pipeline Functions                 │    │
│  │ • process_calibration_file()       │    │
│  │ • train_model()                    │    │
│  │ • process_prediction_window()      │    │
│  └────────────────────────────────────┘    │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │ Serial Handler (Background Thread) │    │
│  │ • serial_reader_thread()           │    │
│  │ • Continuous ADC reading           │    │
│  │ • Data routing (record/predict)    │    │
│  │ • WebSocket emission               │    │
│  └────────────────────────────────────┘    │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │ API Routes                         │    │
│  │ GET  /                             │    │
│  │ GET  /api/ports                    │    │
│  │ POST /api/connect                  │    │
│  │ POST /api/disconnect               │    │
│  │ POST /api/start_recording          │    │
│  │ POST /api/stop_recording           │    │
│  │ POST /api/train_model              │    │
│  │ POST /api/start_prediction         │    │
│  │ POST /api/stop_prediction          │    │
│  │ GET  /api/status                   │    │
│  └────────────────────────────────────┘    │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │ SocketIO Events                    │    │
│  │ • waveform_data (emit)             │    │
│  │ • prediction_data (emit)           │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

---

## Threading Model

```
┌────────────────────────────────────────┐
│         Main Thread (Flask)             │
│                                         │
│  • Handle HTTP requests                │
│  • Route to handlers                   │
│  • Manage WebSocket connections        │
│  • Return responses                    │
│                                         │
│  Spawns:                               │
│    ↓                                   │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│     Serial Reader Thread (Daemon)       │
│                                         │
│  Infinite Loop:                        │
│    1. Check serial port availability   │
│    2. Read incoming byte                │
│    3. Decode ADC value                 │
│    4. Convert to voltage               │
│    5. Add to buffer                    │
│    6. Emit to frontend (if needed)     │
│    7. Process prediction (if active)   │
│    8. Sleep 1ms                        │
│                                         │
│  Thread-Safe Operations:               │
│    • AppState (shared state)           │
│    • SocketIO emit (thread-safe)       │
│    • Serial port (locked)              │
└────────────────────────────────────────┘
```

---

## State Machine

```
┌─────────────┐
│    IDLE     │ (Initial state)
└─────────────┘
       │
       │ User connects to port
       ↓
┌─────────────┐
│  CONNECTED  │
└─────────────┘
       │
       ├─→ Start recording → ┌────────────────┐
       │                      │   RECORDING    │
       │                      │   (calm/active)│
       │                      └────────────────┘
       │                              │
       │                              │ Stop recording
       │                              ↓
       │                      ┌────────────────┐
       │                      │  PROCESSING    │
       │                      │  (automatic)   │
       │                      └────────────────┘
       │                              │
       │                              ↓
       │                      ┌────────────────┐
       │    ┌────────────────→│  CONNECTED     │
       │    │                 │  (data saved)  │
       │    │                 └────────────────┘
       │    │
       │    │ Both datasets collected
       │    ↓
       │ Train model → ┌────────────────┐
       │                │   TRAINING     │
       │                └────────────────┘
       │                        │
       │                        │ Model trained
       │                        ↓
       │                ┌────────────────┐
       │                │  MODEL READY   │
       │                └────────────────┘
       │                        │
       │                        │ Start prediction
       ├───────────────────────→│
       │                        ↓
       │                ┌────────────────┐
       │                │  PREDICTING    │
       │                │  (real-time)   │
       │                └────────────────┘
       │                        │
       │                        │ Stop prediction
       │                        ↓
       ↓                ┌────────────────┐
┌─────────────┐        │  MODEL READY   │
│  CONNECTED  │←───────┘                 │
└─────────────┘                          │
       │                                 │
       │ Disconnect                      │
       ↓                                 │
┌─────────────┐                         │
│    IDLE     │←────────────────────────┘
└─────────────┘
```

---

## File System Structure

```
eeg-calmness-monitor/
│
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                 # Main documentation
├── QUICKSTART.md            # Quick start guide
├── FEATURES.md              # Feature documentation
├── ARCHITECTURE.md          # This file
├── run.sh                   # Linux/Mac startup script
├── run.bat                  # Windows startup script
├── arduino_eeg_sketch.ino   # Arduino code
│
├── templates/
│   └── index.html           # Web interface
│
└── data/                    # Auto-created during runtime
    │
    ├── calibration/         # Raw calibration recordings
    │   ├── calm_raw.csv
    │   └── not_calm_raw.csv
    │
    ├── pipeline_output/     # Processed signals & features
    │   ├── calm_filtered.csv
    │   ├── calm_features.csv
    │   ├── not_calm_filtered.csv
    │   └── not_calm_features.csv
    │
    ├── models/              # Trained ML models
    │   ├── model.pkl
    │   ├── scaler.pkl
    │   └── training_report.txt
    │
    └── results/             # Future: prediction logs
```

---

## Technology Stack

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling with custom properties
- **JavaScript (ES6)**: Application logic
- **Chart.js 4.4**: Real-time charting
- **Socket.IO 4.5**: WebSocket communication

### Backend
- **Python 3.8+**: Core language
- **Flask 3.0**: Web framework
- **Flask-SocketIO 5.3**: WebSocket support
- **PySerial 3.5**: Serial communication
- **NumPy 1.24**: Numerical computing
- **Pandas 2.0**: Data manipulation
- **SciPy 1.11**: Signal processing
- **Scikit-learn 1.3**: Machine learning
- **Joblib 1.3**: Model serialization

### Hardware
- **Arduino**: Data acquisition
- **EEG Sensor**: Neural signal capture
- **USB Serial**: Communication interface

---

## Performance Characteristics

### Latency Analysis
```
Component                    Latency
─────────────────────────────────────
Arduino ADC sampling         4 ms
Serial transmission          < 1 ms
Python serial read           < 1 ms
Voltage conversion           < 0.1 ms
Buffer append                < 0.1 ms
WebSocket emit               < 5 ms
Chart update                 < 10 ms
─────────────────────────────────────
Total (acquisition → display): ~20 ms

Prediction Processing:
─────────────────────────────────────
Filter (500 samples)         5-10 ms
Welch's method               10-20 ms
Feature extraction           < 1 ms
Model prediction             < 1 ms
Result emission              < 5 ms
─────────────────────────────────────
Total (window → prediction): ~40 ms
```

### Resource Usage
```
Memory:
  • Flask server: ~50-100 MB
  • Data buffers: ~10 MB
  • Charts: ~20 MB
  • Total: ~100-150 MB

CPU:
  • Idle: 1-2%
  • Recording: 5-10%
  • Predicting: 10-15%

Disk:
  • Per 5-min recording: ~1-2 MB
  • Model files: < 1 MB
  • Total project: ~5-10 MB
```

---

## Security Considerations

### Current Implementation
- **Local Only**: Runs on localhost
- **No Authentication**: Single user assumed
- **No Encryption**: Local communication only
- **File System**: Unrestricted local access

### Future Enhancements
- User authentication
- HTTPS support
- Data encryption
- Access control
- Session management
- Rate limiting

---

## Scalability

### Current Limitations
- Single user at a time
- Single serial connection
- Local file storage
- In-memory buffering

### Potential Improvements
- Multiple user sessions
- Multiple sensor support
- Database storage (PostgreSQL)
- Cloud deployment
- Load balancing
- Microservices architecture

---

## Testing Strategy

### Unit Tests (Future)
- Signal processing functions
- Feature extraction
- Model training pipeline
- API endpoints

### Integration Tests
- Serial communication
- WebSocket events
- File operations
- Model save/load

### Manual Testing
- Hardware connection
- Data collection
- Real-time prediction
- UI responsiveness

---

## Deployment Options

### Local Development
```bash
python app.py
# Accessible at http://localhost:5000
```

### Production (Future)
```bash
# Using Gunicorn + Nginx
gunicorn -k eventlet -w 1 app:app

# Using Docker
docker build -t eeg-monitor .
docker run -p 5000:5000 --device=/dev/ttyUSB0 eeg-monitor
```

---

## Maintenance & Monitoring

### Logs
- Flask application logs
- Serial communication errors
- Model training reports
- WebSocket events

### Monitoring Points
- Serial connection health
- Data acquisition rate
- Prediction latency
- Model accuracy

### Backup Strategy
- Regular model backups
- Calibration data archives
- Configuration exports

---

**This architecture provides a solid foundation for real-time EEG monitoring and classification! 🧠⚡**