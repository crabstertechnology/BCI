# 🚀 Quick Start Guide - EEG Calmness Monitor

## ⚡ 5-Minute Setup

### Step 1: Install (1 minute)
```bash
pip install -r requirements.txt
```

### Step 2: Connect Hardware (1 minute)
1. Connect EEG sensor to Arduino pin A0
2. Upload `arduino_eeg_sketch.ino` to Arduino
3. Connect Arduino to computer via USB

### Step 3: Run Application (30 seconds)
```bash
python app.py
```
Open browser: `http://localhost:5000`

### Step 4: Connect to Arduino (30 seconds)
1. Select your Arduino port from dropdown
2. Click "Connect" button
3. Wait for green "Connected" status

### Step 5: Collect Calibration Data (10 minutes)

**CALM Session (5 minutes):**
1. Click "Record Calm"
2. Relax, close eyes, breathe deeply
3. Stay still
4. After 5 minutes → Click "Stop Recording"

**NOT CALM Session (5 minutes):**
1. Click "Record Not Calm"
2. Do mental math, read, or move around
3. Stay active
4. After 5 minutes → Click "Stop Recording"

### Step 6: Train Model (30 seconds)
1. Click "Train Model"
2. Wait for "Model trained successfully!" message
3. Check accuracy in message

### Step 7: Real-Time Prediction (Ongoing)
1. Click "Start Prediction"
2. Watch live classification:
   - **Green = CALM** (relaxed state)
   - **Magenta = NOT CALM** (active state)
3. View live waveform and features
4. Click "Stop Prediction" when done

---

## 🎯 Tips for Best Results

### ✅ DO:
- Collect 5-10 minutes per state
- Keep electrode contact stable
- Use consistent environment
- Create distinct mental states
- Wait for "Connected" before recording

### ❌ DON'T:
- Move during calm recording
- Record in noisy electrical environments
- Use poor electrode contact
- Mix mental states during recording
- Disconnect during training

---

## 📊 What You'll See

### Status Bar (Top)
- **Connection**: Green = Connected to Arduino
- **Mode**: Shows Recording/Predicting/Idle
- **Model Status**: Shows if model is trained
- **Calibration Data**: Shows which data you've collected

### Live Waveform
- Real-time EEG voltage signal
- Updates continuously during recording/prediction
- Blue line shows clean signal

### Feature Analysis (Prediction Mode)
- Green = Alpha power
- Magenta = Beta power  
- Orange = α/β Ratio
- Higher ratio = More calm

### Prediction Display
- Large text: Current state
- Three metrics: Alpha, Beta, Ratio
- Color changes with state

---

## 🔥 Common Issues - Quick Fixes

**"No ports available"**
→ Plug in Arduino, refresh page

**"Connection failed"**
→ Close Arduino IDE Serial Monitor

**"Model not trained"**
→ Collect both calm and not calm data first

**"Poor accuracy"**
→ Collect more data, ensure distinct states

**Waveform not moving**
→ Check Arduino connection, verify sketch uploaded

---

## 📱 Interface Overview

```
┌─────────────────────────────────────────┐
│  🧠 EEG CALMNESS MONITOR                │
├─────────────────────────────────────────┤
│ Status: ✓Connected  Mode: Predicting   │
├──────────────┬──────────────────────────┤
│ CONNECTION   │  CALIBRATION             │
│ Port: COM3   │  [Record Calm]           │
│ [Connect]    │  [Record Not Calm]       │
├──────────────┴──────────────────────────┤
│ TRAINING                                │
│ [Train Model] ← Do after collecting data│
├─────────────────────────────────────────┤
│ PREDICTION                              │
│ [Start] [Stop]                          │
│                                         │
│        ╔═══════════════╗                │
│        ║   NOT CALM    ║                │
│        ╚═══════════════╝                │
│   Alpha: 2.3e-10  Beta: 8.1e-10        │
│           Ratio: 0.284                  │
├─────────────────────────────────────────┤
│ 📈 LIVE WAVEFORM                        │
│ [Scrolling EEG signal graph]            │
├─────────────────────────────────────────┤
│ 📉 FEATURE ANALYSIS                     │
│ [Alpha/Beta/Ratio over time]            │
└─────────────────────────────────────────┘
```

---

## 🎓 Understanding the Results

### Alpha/Beta Ratio Interpretation:
- **> 1.0**: Very Calm (strong alpha dominance)
- **0.5 - 1.0**: Calm (moderate alpha)
- **0.3 - 0.5**: Not Calm (beta dominance)
- **< 0.3**: Very Active (strong beta)

### Typical Values:
```
CALM State:
  Alpha: High (1e-9 to 1e-8)
  Beta: Low (1e-10 to 1e-9)
  Ratio: 0.8 - 2.0

NOT CALM State:
  Alpha: Low (1e-10 to 1e-9)
  Beta: High (1e-9 to 1e-8)
  Ratio: 0.1 - 0.5
```

---

## 🚨 Emergency Troubleshooting

**Application Won't Start:**
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

**Can't Connect to Port:**
```bash
# Linux: Add user to dialout group
sudo usermod -a -G dialout $USER
# Then logout and login

# Windows: Check Device Manager for correct COM port
```

**Data Collection Fails:**
1. Check Arduino is running (LED blinking?)
2. Open Arduino Serial Monitor briefly to verify data
3. Close Serial Monitor
4. Reconnect in web app

---

## 📞 Need Help?

1. ✅ Read main README.md for details
2. ✅ Check Troubleshooting section
3. ✅ Verify hardware connections
4. ✅ Test Arduino sketch independently
5. ✅ Open issue on repository

---

**Remember**: The first run requires ~15 minutes total:
- 10 min: Calibration data collection
- 30 sec: Model training  
- Then: Unlimited real-time prediction!

**Pro Tip**: Save your trained model! Once trained, you can immediately start prediction in future sessions without recalibrating (unless you change electrode positions).