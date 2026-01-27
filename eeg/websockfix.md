# 🔌 WebSocket Connection Fix - Diagnostic Guide

## What Was Fixed

### Issue
Predictions were working in the Python terminal but not showing in the web browser.

### Root Cause
WebSocket events were not being broadcast properly from the background thread to the frontend.

### Fixes Applied

1. **Added `broadcast=True` to all emit calls**
   - Ensures events reach all connected clients
   - Required when emitting from background threads

2. **Added WebSocket connection handlers**
   - Logs when clients connect/disconnect
   - Helps debug connection issues

3. **Added frontend debugging**
   - Console.log messages for all WebSocket events
   - Connection status monitoring

4. **Improved SocketIO configuration**
   - Added threading mode
   - Enabled logger for debugging

## How to Test

### Step 1: Update Files
1. Stop current app (CTRL+C)
2. Replace `app.py` with new version
3. Replace `templates/index.html` with new version
4. Restart: `python app.py`

### Step 2: Check Terminal Output
You should see:
```
============================================================
EEG CALMNESS MONITOR - Web Application
============================================================

Open your browser and navigate to: http://localhost:5000

Press CTRL+C to stop the server

[followed by Flask-SocketIO startup messages]
```

### Step 3: Open Browser
1. Navigate to http://localhost:5000
2. Press F12 to open Developer Console
3. Look for:
```
✅ WebSocket connected!
Socket ID: [some ID]
📡 Server response: {data: 'Connected to EEG Monitor'}
```

### Step 4: Connect Arduino & Start Prediction
1. Select COM port
2. Click "Connect"
3. Click "Start Prediction"

### Step 5: Verify Data Flow

**In Terminal (Python):**
```
============================================================
PREDICTION MODE STARTED
============================================================
Model loaded: data\models\model.pkl
...

WebSocket CLIENT CONNECTED
============================================================

[Prediction] Calm | α=8.21e-06 β=3.11e-06 ratio=2.641 conf=91.2%
[WebSocket] Emitting prediction_data: Calm
[Prediction] Not Calm | α=4.92e-06 β=5.75e-06 ratio=0.856 conf=72.3%
[WebSocket] Emitting prediction_data: Not Calm
```

**In Browser Console (F12):**
```
📊 Waveform data received: 2.34 0.523
🔮 Prediction received: Calm ratio: 2.641
🔮 Prediction received: Not Calm ratio: 0.856
```

**On Dashboard:**
- Display should change between "CALM" (green) and "NOT CALM" (magenta)
- Metrics should update every 0.5 seconds
- Live waveform should scroll
- Feature chart should update

## Troubleshooting

### If WebSocket Still Not Connecting

1. **Check browser console for errors**
   ```javascript
   // Look for:
   ❌ WebSocket connection error: [error message]
   ```

2. **Try different browser**
   - Chrome/Edge recommended
   - Clear cache and cookies

3. **Check firewall**
   - Allow Python through Windows Firewall
   - Temporarily disable antivirus

4. **Verify SocketIO version**
   ```bash
   pip show flask-socketio
   # Should be 5.3.5 or higher
   ```

5. **Try different port**
   - Edit app.py, change last line:
   ```python
   socketio.run(app, debug=False, host='0.0.0.0', port=5001)
   ```
   - Then browse to http://localhost:5001

### If Data Not Showing in Dashboard

1. **Check prediction is running**
   - Terminal should show `[Prediction]` messages
   - Terminal should show `[WebSocket] Emitting...` messages

2. **Check browser console**
   - Should see `🔮 Prediction received:` messages
   - If not, WebSocket issue

3. **Refresh page**
   - Hard refresh: CTRL+F5
   - Reconnect to port
   - Start prediction again

### If Terminal Shows WebSocket Emit But Browser Doesn't Receive

1. **Check namespace**
   - All emits should have `namespace='/'`
   - Browser should connect to default namespace

2. **Check broadcast flag**
   - All background thread emits need `broadcast=True`

3. **Restart everything**
   ```bash
   # Stop app (CTRL+C)
   # Close browser
   # Restart app
   python app.py
   # Open fresh browser window
   ```

## Expected Behavior After Fix

### Terminal Output
```
[Status] Rate: 100.6 Hz, Buffer: 500, Predictions: 10

[Prediction] Not Calm | α=5.38e-06 β=8.11e-06 ratio=0.664 conf=58.5%
[WebSocket] Emitting prediction_data: Not Calm

[Prediction] Calm | α=3.15e-05 β=3.55e-05 ratio=0.886 conf=50.2%
[WebSocket] Emitting prediction_data: Calm
```

### Browser Console (F12)
```
✅ WebSocket connected!
Socket ID: abc123xyz
📡 Server response: {data: 'Connected to EEG Monitor'}
📊 Waveform data received: 2.34 0.523
📊 Waveform data received: 2.84 0.517
🔮 Prediction received: Not Calm ratio: 0.664
🔮 Prediction received: Calm ratio: 0.886
```

### Web Dashboard
```
┌─────────────────────────┐
│    🟢 CALM              │  ← Changes every 0.5s
│  Alpha: 3.15e-05        │  ← Updates
│  Beta: 3.55e-05         │  ← Updates  
│  Ratio: 0.886           │  ← Updates
└─────────────────────────┘
```

## Quick Verification Commands

```bash
# 1. Check Python packages
pip show flask-socketio

# 2. Run app with debug
python app.py

# 3. In browser console (F12), check connection:
socket.connected
# Should return: true

# 4. Check socket events:
socket.onAny((event, ...args) => {
    console.log('Event:', event, 'Args:', args);
});
```

## Success Criteria

✅ Terminal shows "WebSocket CLIENT CONNECTED"
✅ Browser console shows "✅ WebSocket connected!"
✅ Terminal shows "[WebSocket] Emitting prediction_data"
✅ Browser console shows "🔮 Prediction received"
✅ Dashboard display changes between states
✅ Metrics update every 0.5 seconds

## If All Else Fails

Try this minimal test:

1. **Create test.html in project folder:**
```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>
<body>
    <h1>WebSocket Test</h1>
    <div id="status">Connecting...</div>
    <div id="data"></div>
    <script>
        const socket = io();
        socket.on('connect', () => {
            document.getElementById('status').textContent = 'Connected!';
        });
        socket.on('prediction_data', (data) => {
            document.getElementById('data').textContent = 
                'Prediction: ' + data.state + ' | Ratio: ' + data.ratio;
        });
    </script>
</body>
</html>
```

2. **Open test.html in browser while app is running**
3. **Start prediction**
4. **Should see predictions updating**

If this works but main app doesn't, it's a frontend JS issue.
If this doesn't work, it's a backend WebSocket issue.

---

**The fix is now applied - restart your app and check the browser console!** 🎉