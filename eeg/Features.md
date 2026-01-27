# 🎯 Feature Documentation - EEG Calmness Monitor

## Overview
This document provides detailed information about all features in the EEG Calmness Monitor web application.

---

## 🔌 1. Port Selection & Connection

### Port Detection
- **Automatic Discovery**: Application automatically scans for available serial ports
- **Real-time Updates**: Port list refreshes on page load
- **Cross-Platform**: Works on Windows (COMx), Linux (/dev/ttyUSBx), and macOS (/dev/cu.*)

### Connection Management
```
Features:
✓ One-click connection
✓ Connection status indicator
✓ Automatic disconnection on error
✓ Prevention of multiple connections
✓ Port locking during operation
```

**Visual Feedback:**
- Green pulsing indicator when connected
- Port name displayed in status bar
- Connect/Disconnect button states change automatically

---

## 📊 2. Live Waveform Visualization

### Real-Time Display
- **Update Rate**: Matches serial data rate (~250 Hz)
- **Display Buffer**: Shows last 500 samples (2 seconds)
- **Smooth Scrolling**: Continuous left-to-right animation
- **Zero Latency**: Direct rendering from serial stream

### Waveform Modes

#### Recording Mode
```
Purpose: Visual feedback during calibration
Display: Raw filtered EEG voltage
Color: Cyan (#00e5ff)
Update: Every sample received
Uses: Verify signal quality, detect artifacts
```

#### Prediction Mode
```
Purpose: Monitor ongoing brain activity
Display: Same signal, different context
Color: Cyan (#00e5ff)
Update: Every sample received
Uses: Confirm sensor contact, real-time monitoring
```

### Technical Details
- **Chart Type**: Line chart with smooth tension
- **Y-Axis**: Voltage in Volts (V)
- **X-Axis**: Time in seconds
- **Fill**: Semi-transparent area under curve
- **Grid**: Dark theme optimized

---

## 🎙️ 3. Start/Stop Recording Buttons

### Two Recording Modes

#### CALM Recording
```
Button: Green "Record Calm"
Purpose: Capture baseline relaxed state
Duration: Recommended 5-10 minutes
Instructions:
  • Close eyes
  • Relax muscles
  • Breathe deeply and slowly
  • Minimize movement
  • Clear your mind
```

#### NOT CALM Recording
```
Button: Orange "Record Not Calm"  
Purpose: Capture active/stressed state
Duration: Recommended 5-10 minutes
Instructions:
  • Perform mental arithmetic
  • Read challenging text
  • Solve puzzles
  • Light physical movement
  • Focused concentration tasks
```

### Recording Process
1. **Click Start**: Recording begins immediately
2. **Live Feedback**: Waveform updates in real-time
3. **Status Update**: Mode indicator shows current session
4. **Click Stop**: Recording ends, processing begins
5. **Automatic Processing**: 
   - ADC to voltage conversion
   - Bandpass filtering (0.5-40 Hz)
   - Notch filtering (50 Hz)
   - Feature extraction (sliding windows)
   - Feature file saved automatically

### File Outputs
```
Location: data/calibration/
Files Created:
  - calm_raw.csv (or not_calm_raw.csv)
    Columns: Time(s), ADC

Location: data/pipeline_output/
Files Created:
  - calm_filtered.csv (or not_calm_filtered.csv)
    Columns: Time(s), Filtered_Voltage
  
  - calm_features.csv (or not_calm_features.csv)
    Columns: Window, Alpha, Beta, AlphaBetaRatio
```

---

## 🧪 4. Data Processing Pipeline

### Stage 1: Signal Acquisition
```python
Input: Raw ADC values (0-4095)
Process: 
  1. Serial communication at 115200 baud
  2. Decode ASCII integer values
  3. Buffer in memory
Output: Digital signal stream
```

### Stage 2: Voltage Conversion
```python
Formula: voltage = (ADC / ADC_MAX) * VREF
Example: (2048 / 4095) * 3.3 = 1.65V
Output: Voltage signal in Volts
```

### Stage 3: Bandpass Filtering
```python
Type: 4th order Butterworth
Passband: 0.5 - 40 Hz
Purpose: 
  • Remove DC offset (< 0.5 Hz)
  • Remove high-frequency noise (> 40 Hz)
  • Preserve EEG frequency bands
Method: Zero-phase filtfilt (forward-backward)
```

### Stage 4: Notch Filtering
```python
Type: IIR Notch Filter
Frequency: 50 Hz (or 60 Hz for North America)
Q Factor: 30
Purpose: Remove power line interference
Method: Zero-phase filtfilt
```

### Stage 5: Windowing
```python
Window Size: 2.0 seconds (500 samples @ 250 Hz)
Step Size: 0.5 seconds (125 samples)
Overlap: 75%
Total Windows: (signal_length - window_size) / step_size
```

### Stage 6: Power Spectral Density
```python
Method: Welch's method
FFT Size: 512 points
Window: Hanning
Output: Frequency vs Power
Resolution: ~0.49 Hz per bin
```

### Stage 7: Feature Extraction
```python
Alpha Band: 8-13 Hz
  • Associated with relaxation
  • Integrated power using trapezoidal rule

Beta Band: 13-30 Hz
  • Associated with active thinking
  • Integrated power using trapezoidal rule

Alpha/Beta Ratio:
  • Primary feature for classification
  • Higher = More calm
  • Lower = More active
```

---

## 🤖 5. Machine Learning Model

### Training Pipeline

#### Step 1: Data Loading
```python
Load: calm_features.csv + not_calm_features.csv
Features: [Alpha, Beta, AlphaBetaRatio]
Labels: ["Calm", "Not Calm"]
```

#### Step 2: Data Preparation
```python
• Combine datasets
• Add labels
• Shuffle (random_state=42)
• Split 70% train / 30% test
• Stratify by class (maintain balance)
```

#### Step 3: Feature Scaling
```python
Method: StandardScaler
Process: 
  • Calculate mean and std from training data
  • Transform: (x - mean) / std
  • Apply same transform to test data
Benefits:
  • Prevents feature dominance
  • Improves convergence
  • Required for logistic regression
```

#### Step 4: Model Training
```python
Algorithm: Logistic Regression
Parameters:
  • max_iter: 1000
  • class_weight: 'balanced'
  • solver: 'lbfgs' (default)
  
Class Weighting:
  • Automatically adjusts for imbalanced data
  • weight = n_samples / (n_classes * n_samples_class)
```

#### Step 5: Evaluation
```python
Metrics:
  • Accuracy: Overall correctness
  • Precision: True positives / Predicted positives
  • Recall: True positives / Actual positives
  • F1-Score: Harmonic mean of precision/recall
  
Confusion Matrix:
  • True Calm, True Not Calm (correct)
  • False Calm, False Not Calm (errors)
```

### Model Files
```
Location: data/models/
Files:
  • model.pkl: Trained classifier
  • scaler.pkl: Feature scaler
  • training_report.txt: Evaluation metrics
```

---

## 🔮 6. Real-Time Prediction

### Prediction Flow
```
1. Serial Data → Buffer (continuous)
2. Buffer reaches 500 samples (2 seconds)
3. Apply bandpass + notch filters
4. Welch's method → PSD
5. Extract alpha and beta power
6. Calculate α/β ratio
7. Scale features using saved scaler
8. Predict using trained model
9. Display result + confidence
10. Slide buffer by 125 samples (0.5s)
11. Repeat from step 2
```

### Update Frequency
- **Window**: Every 2 seconds
- **Step**: Every 0.5 seconds
- **Predictions**: ~2 per second
- **Latency**: < 100ms processing time

### Display Components

#### State Indicator
```
CALM State:
  • Color: Green (#00ff88)
  • Border: Green glow
  • Background: Green tint
  • Font: Large, bold
  
NOT CALM State:
  • Color: Magenta (#ff00aa)
  • Border: Magenta glow
  • Background: Magenta tint
  • Font: Large, bold
```

#### Metrics Panel
```
Alpha Power:
  • Format: Scientific notation
  • Units: Power spectral density
  • Typical: 1e-10 to 1e-8

Beta Power:
  • Format: Scientific notation
  • Units: Power spectral density
  • Typical: 1e-10 to 1e-8

α/β Ratio:
  • Format: 3 decimal places
  • Units: Dimensionless
  • Range: 0.1 to 3.0
  • Calm: > 0.8
  • Not Calm: < 0.5
```

---

## 📈 7. Feature Analysis Chart

### Real-Time Visualization
- **Update**: Every prediction (~0.5 seconds)
- **Display**: Last 50 windows (25 seconds)
- **Type**: Multi-line chart with dual Y-axes

### Chart Components

#### Alpha Power Line
```
Color: Green (#00ff88)
Y-Axis: Left (Power)
Interpretation:
  • Peaks during relaxation
  • Drops during activity
  • Should increase in calm state
```

#### Beta Power Line
```
Color: Magenta (#ff00aa)
Y-Axis: Left (Power)
Interpretation:
  • Peaks during concentration
  • Drops during relaxation
  • Should increase in active state
```

#### α/β Ratio Line
```
Color: Orange (#ff8800)
Y-Axis: Right (Ratio)
Interpretation:
  • Primary classification feature
  • High = Calm
  • Low = Not Calm
  • Shows state transitions
```

### Use Cases
- **Monitoring Trends**: See changes over time
- **Validating States**: Confirm model decisions
- **Debugging**: Identify sensor issues
- **Analysis**: Study personal patterns

---

## 🎛️ 8. Status Dashboard

### Four Status Indicators

#### 1. Connection Status
```
States:
  Disconnected: Gray indicator, "Disconnected"
  Connected: Green pulsing, Port name (e.g., "COM3")
  
Information:
  • Current serial port
  • Connection health
  • Enable/disable actions
```

#### 2. Mode Status
```
States:
  Idle: No active operation
  Recording (calm): Currently recording calm data
  Recording (not_calm): Currently recording active data
  Predicting: Real-time classification active
  
Visual: Active state highlighted
```

#### 3. Model Status
```
States:
  Not Trained: No model available
  Trained: Model ready for prediction
  
Information:
  • Model availability
  • Enable prediction mode
```

#### 4. Calibration Data Status
```
States:
  None: No data collected
  Calm: Only calm data available
  Not Calm: Only active data available
  Calm + Not Calm: Both datasets ready
  
Information:
  • Which datasets exist
  • Enable model training
```

---

## 🎨 9. User Interface Features

### Design Philosophy
- **Neuroscience-Inspired**: Brain wave aesthetic
- **High Contrast**: Dark theme for long sessions
- **Clear Feedback**: Immediate visual responses
- **Professional**: Clinical monitoring appearance

### Color Scheme
```
Background: Deep dark blue (#0a0e17)
Panels: Midnight blue (#131820)
Accents:
  • Cyan: Technology, connection (#00e5ff)
  • Green: Calm state, success (#00ff88)
  • Magenta: Active state, warnings (#ff00aa)
  • Orange: Alerts, ratios (#ff8800)
```

### Typography
```
Headers: Orbitron (futuristic, tech)
Body: IBM Plex Mono (clinical, data)
Sizes: Responsive, hierarchical
```

### Animations
```
• Gradient background shift (20s cycle)
• Scanner line in header (3s)
• Button hover effects
• Status indicator pulse (2s)
• Chart smooth updates
• Message slide-in
```

### Responsive Design
- **Desktop**: Full dual-panel layout
- **Tablet**: Single column with large controls
- **Mobile**: Optimized touch targets

---

## 🔒 10. Safety & Reliability Features

### Error Handling
```
Serial Errors:
  • Auto-disconnect on failure
  • Clear error messages
  • Reconnection support

Processing Errors:
  • Skip invalid windows
  • Continue on single failures
  • Log errors to console

Model Errors:
  • Validate data before training
  • Check model existence
  • Graceful degradation
```

### Data Integrity
```
• CSV files include headers
• Timestamps for all samples
• Automatic folder creation
• File overwrite protection
• Valid data type checking
```

### User Protection
```
• Disabled buttons during operations
• Confirmation via messages
• Clear state indicators
• Cannot start conflicting operations
• Safe stop at any time
```

---

## 📊 11. Data Export & Analysis

### Saved Data Files

#### Raw Calibration
```
File: calm_raw.csv, not_calm_raw.csv
Format: Time(s), ADC
Use: Raw backup, reprocessing
```

#### Filtered Signals
```
File: calm_filtered.csv, not_calm_filtered.csv
Format: Time(s), Filtered_Voltage
Use: Signal quality assessment
```

#### Extracted Features
```
File: calm_features.csv, not_calm_features.csv
Format: Window, Alpha, Beta, AlphaBetaRatio
Use: Model training, analysis
```

#### Model Assets
```
Files: model.pkl, scaler.pkl
Format: Pickle (scikit-learn)
Use: Real-time prediction
```

#### Training Report
```
File: training_report.txt
Content:
  • Training date
  • Sample counts
  • Test accuracy
  • Classification report
  • Confusion matrix
```

---

## 🚀 Advanced Features

### Future Enhancements
- Export prediction logs
- Session history
- Multiple user profiles
- Advanced visualizations
- Frequency spectrum display
- Artifact rejection
- Adaptive thresholds
- Mobile app integration

---

## 📞 Support

For feature requests, bug reports, or questions:
1. Check this documentation
2. Review README.md
3. See QUICKSTART.md
4. Open GitHub issue

**Enjoy monitoring your brain waves! 🧠✨**