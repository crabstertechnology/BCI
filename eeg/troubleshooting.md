# 🔧 Troubleshooting Guide - EEG Calmness Monitor

## Common Issues and Solutions

### 1. Serial Connection Errors

#### Error: "Serial read error: 'NoneType' object has no attribute 'hEvent'"
**Cause**: This is a harmless warning that appears before connecting to the Arduino.

**Solution**: 
- ✅ **No action needed** - This error disappears once you connect to a port
- The application is designed to handle this gracefully
- It's just the background thread checking for a connection

#### Error: "No ports available"
**Solutions**:
1. **Check USB connection**
   - Verify Arduino is plugged in
   - Try a different USB cable
   - Try a different USB port

2. **Install drivers** (Windows)
   ```
   - Download Arduino drivers from arduino.cc
   - Install CH340/CP2102 drivers if using clone boards
   ```

3. **Check permissions** (Linux)
   ```bash
   # Add user to dialout group
   sudo usermod -a -G dialout $USER
   # Logout and login again
   ```

4. **Verify device** (Mac)
   ```bash
   ls /dev/cu.*
   # Should show Arduino port like /dev/cu.usbserial-*
   ```

#### Error: "Connection failed"
**Solutions**:
1. **Close Arduino IDE Serial Monitor**
   - Port can only be used by one application
   - Close Serial Monitor in Arduino IDE
   - Disconnect from any other serial terminal

2. **Check baud rate**
   - Arduino sketch should use 115200 baud
   - Verify in the sketch: `Serial.begin(115200);`

3. **Verify Arduino sketch is uploaded**
   - Re-upload arduino_eeg_sketch.ino
   - Check for upload success message

4. **Restart application**
   - Stop the Python server (CTRL+C)
   - Restart: `python app.py`

---

### 2. Data Collection Issues

#### Warning: "nperseg = 512 is greater than input length"
**Cause**: Short calibration recordings (less than 2 seconds).

**Solutions**:
- ✅ **Usually harmless** - The code auto-adjusts nperseg
- **For best results**: Record at least 5 minutes per session
- **Fixed in latest version**: nperseg now auto-adjusts to window size

#### No waveform showing during recording
**Solutions**:
1. **Check serial connection**
   - Status bar should show "Connected" with green indicator
   - Verify Arduino is sending data

2. **Test Arduino independently**
   ```
   - Open Arduino Serial Monitor (temporarily)
   - Should see numbers scrolling (0-4095)
   - Close Serial Monitor before using app
   ```

3. **Check browser console**
   - Press F12 in browser
   - Look for JavaScript errors
   - Refresh page if needed

#### Recording stops immediately
**Solutions**:
1. **Verify connection before recording**
   - Wait for "Connected" status
   - Don't click record before connecting

2. **Check serial data**
   - Arduino should continuously send data
   - Verify with Serial Monitor test

---

### 3. Model Training Issues

#### Error: "Missing calibration data"
**Cause**: Both calm and not calm datasets must be collected.

**Solutions**:
1. **Collect both datasets**
   - Record "Calm" session (5+ minutes)
   - Record "Not Calm" session (5+ minutes)
   - Status bar will show "Calm + Not Calm"

2. **Verify files exist**
   ```
   Check these files:
   - data/calibration/calm_raw.csv
   - data/calibration/not_calm_raw.csv
   ```

3. **Re-record if needed**
   - Previous recordings are overwritten
   - Safe to record again

#### Low training accuracy (< 70%)
**Causes and Solutions**:

1. **Insufficient data**
   - ✅ Collect 10-15 minutes per state
   - More data = better accuracy

2. **Similar mental states**
   - ❌ Don't: Sit quietly for both sessions
   - ✅ Do: Very calm vs very active
   - **Calm**: Eyes closed, relaxed, meditative
   - **Not Calm**: Mental math, reading, movement

3. **Poor electrode contact**
   - Clean electrodes
   - Use conductive gel if available
   - Ensure stable contact throughout

4. **Environmental noise**
   - Record in quiet environment
   - Minimize movement
   - Avoid electrical interference

---

### 4. Prediction Issues

#### Error: "Model not trained yet"
**Solution**: 
1. Collect both calm and not calm data
2. Click "Train Model"
3. Wait for success message
4. Then start prediction

#### Predictions not updating
**Solutions**:
1. **Check connection**
   - Must be connected to Arduino
   - Verify live waveform is updating

2. **Verify model loaded**
   - Status should show "Model: Trained"
   - Check files exist:
     ```
     - data/models/model.pkl
     - data/models/scaler.pkl
     ```

3. **Restart prediction**
   - Click "Stop Prediction"
   - Click "Start Prediction" again

#### Predictions seem random/incorrect
**Causes and Solutions**:

1. **Poor calibration**
   - Re-collect calibration data
   - Ensure distinct mental states
   - 10+ minutes each session

2. **Changed electrode position**
   - Electrodes should be in same position as calibration
   - Re-calibrate if position changed

3. **Noisy signal**
   - Check waveform for artifacts
   - Minimize movement during prediction
   - Ensure good electrode contact

---

### 5. Web Interface Issues

#### Page not loading
**Solutions**:
1. **Check server is running**
   ```
   Terminal should show:
   "Running on http://localhost:5000"
   ```

2. **Correct URL**
   - Use: http://localhost:5000
   - Not: https://localhost:5000

3. **Try different browser**
   - Chrome/Edge recommended
   - Clear browser cache

4. **Check firewall**
   - Allow Python through firewall
   - Temporarily disable antivirus

#### Charts not displaying
**Solutions**:
1. **Check internet connection** (for Chart.js CDN)
   - Charts require internet for CDN libraries
   - Or host Chart.js locally

2. **Browser console errors**
   - Press F12 → Console tab
   - Look for red errors
   - Report if persistent

3. **Refresh page**
   - Hard refresh: CTRL+F5 (Windows) or CMD+Shift+R (Mac)

#### Buttons not responding
**Solutions**:
1. **Check status requirements**
   - Must be connected for recording
   - Must have data for training
   - Must have model for prediction

2. **Look for error messages**
   - Messages appear below each panel
   - Read error descriptions

3. **Refresh page**
   - F5 to reload
   - Reconnect to port

---

### 6. Performance Issues

#### Application running slow
**Solutions**:
1. **Close other applications**
   - Free up system resources
   - Close unnecessary browser tabs

2. **Reduce buffer sizes** (in app.py)
   ```python
   # Change this line:
   self.buffer = deque(maxlen=int(FS * 10))  # 10 seconds
   # To:
   self.buffer = deque(maxlen=int(FS * 5))   # 5 seconds
   ```

3. **Lower chart update frequency** (in index.html)
   ```javascript
   // Reduce displayed points
   if (waveformChart.data.labels.length > 500)  // Default
   // To:
   if (waveformChart.data.labels.length > 250)  // Faster
   ```

#### High CPU usage
**Solutions**:
1. **Normal during prediction** (10-15% CPU is expected)
2. **Check for infinite loops** in console
3. **Restart application** if usage > 50%

---

### 7. File System Issues

#### Error: "Cannot create directory"
**Solutions**:
1. **Check permissions**
   - Run as administrator (Windows)
   - Use sudo if needed (Linux/Mac)

2. **Disk space**
   - Ensure at least 100MB free
   - Clean old recordings if needed

3. **Path issues**
   - Don't run from network drive
   - Use local disk

#### Data files not saving
**Solutions**:
1. **Check console for errors**
   - Look in terminal running Python

2. **Verify write permissions**
   ```bash
   # Linux/Mac
   chmod -R 755 data/
   ```

3. **Manual directory creation**
   ```bash
   mkdir -p data/calibration
   mkdir -p data/pipeline_output
   mkdir -p data/models
   mkdir -p data/results
   ```

---

### 8. Python/Dependency Issues

#### ImportError: "No module named 'flask'"
**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt

# Or manually:
pip install flask flask-socketio pyserial numpy pandas scipy scikit-learn joblib eventlet
```

#### Version conflicts
**Solutions**:
1. **Use virtual environment** (recommended)
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Update pip**
   ```bash
   pip install --upgrade pip
   ```

#### Python version too old
**Requirements**: Python 3.8 or higher

**Check version**:
```bash
python --version
```

**Install newer Python**:
- Windows: Download from python.org
- Mac: `brew install python@3.11`
- Linux: `sudo apt install python3.11`

---

### 9. Arduino Issues

#### Arduino not recognized
**Solutions**:
1. **Install drivers**
   - Official Arduino: Auto-installs
   - Clone boards: Install CH340 or CP2102 drivers

2. **Try different cable**
   - Some cables are power-only (no data)
   - Use a data-capable USB cable

3. **Check board in Device Manager** (Windows)
   - Should show as COM port
   - Update driver if needed

#### Garbled/random serial data
**Solutions**:
1. **Check baud rate matches**
   - Arduino: 115200
   - Python: 115200

2. **Reset Arduino**
   - Press reset button
   - Or disconnect/reconnect USB

3. **Re-upload sketch**
   - Verify upload was successful
   - Check for compilation errors

---

### 10. Getting Help

#### Still having issues?

1. **Check all documentation**
   - README.md
   - QUICKSTART.md
   - FEATURES.md
   - ARCHITECTURE.md

2. **Enable debug mode** (app.py)
   ```python
   # Change this line:
   socketio.run(app, debug=False, host='0.0.0.0', port=5000)
   # To:
   socketio.run(app, debug=True, host='0.0.0.0', port=5000)
   ```

3. **Collect diagnostic info**
   ```
   - Python version
   - Operating system
   - Error messages (full text)
   - Console output
   - Browser console errors
   ```

4. **Test components independently**
   - Test Arduino Serial Monitor
   - Test Python serial connection
   - Test web interface without Arduino

---

## Quick Diagnostic Checklist

Run through this checklist to identify issues:

- [ ] Python 3.8+ installed?
- [ ] All dependencies installed?
- [ ] Arduino connected via USB?
- [ ] Arduino sketch uploaded?
- [ ] Serial Monitor closed?
- [ ] Correct port selected?
- [ ] "Connected" status showing?
- [ ] Waveform updating during recording?
- [ ] Both datasets collected?
- [ ] Model trained successfully?
- [ ] Browser at http://localhost:5000?
- [ ] No JavaScript errors in console?

---

## Error Code Reference

| Error Message | Cause | Solution |
|--------------|-------|----------|
| "No ports available" | Arduino not detected | Check USB, install drivers |
| "Connection failed" | Port in use | Close Serial Monitor |
| "Missing calibration data" | Incomplete data collection | Record both sessions |
| "Model not trained yet" | No trained model | Train model first |
| "Serial read error" | Before connection | Normal, ignore |
| "Prediction error" | Signal processing issue | Check electrode contact |

---

## Prevention Tips

**Avoid common issues:**

1. ✅ **Always close Arduino Serial Monitor** before using app
2. ✅ **Collect sufficient data** (5-10 minutes minimum)
3. ✅ **Create distinct mental states** during calibration
4. ✅ **Maintain electrode position** between sessions
5. ✅ **Use stable power supply** for Arduino
6. ✅ **Record in quiet environment**
7. ✅ **Keep electrodes clean**
8. ✅ **Test components individually** before full system

---

**If you've tried everything and still have issues, create a detailed bug report with:**
- Exact error message
- Steps to reproduce
- System information
- Screenshots if helpful

Happy troubleshooting! 🔧✨