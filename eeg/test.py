#!/usr/bin/env python3
"""
EEG Monitor - Serial Diagnostic Tool
Tests serial connection and data flow
"""

import serial
import serial.tools.list_ports
import time
import sys

print("="*60)
print("EEG MONITOR - SERIAL DIAGNOSTIC TOOL")
print("="*60)

# List available ports
print("\n1. Available Serial Ports:")
print("-" * 40)
ports = list(serial.tools.list_ports.comports())
if not ports:
    print("❌ No serial ports found!")
    print("   - Check Arduino is connected")
    print("   - Try different USB port")
    sys.exit(1)

for i, port in enumerate(ports):
    print(f"   [{i}] {port.device} - {port.description}")

# Select port
print("\n2. Select Port:")
print("-" * 40)
try:
    selection = int(input("Enter port number: "))
    selected_port = ports[selection].device
    print(f"✓ Selected: {selected_port}")
except (ValueError, IndexError):
    print("❌ Invalid selection")
    sys.exit(1)

# Test connection
print("\n3. Testing Connection:")
print("-" * 40)
try:
    ser = serial.Serial(selected_port, 115200, timeout=1)
    print(f"✓ Connected to {selected_port}")
    time.sleep(2)  # Wait for Arduino to reset
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)

# Test data reception
print("\n4. Testing Data Reception (10 seconds):")
print("-" * 40)
print("Receiving data...")

samples = []
start_time = time.time()
errors = 0

try:
    while time.time() - start_time < 10:
        if ser.in_waiting:
            try:
                raw = ser.readline().decode(errors="ignore").strip()
                if raw.isdigit():
                    value = int(raw)
                    samples.append(value)
                    
                    # Print progress every second
                    if len(samples) % 250 == 0:
                        elapsed = time.time() - start_time
                        rate = len(samples) / elapsed
                        print(f"   Samples: {len(samples)}, Rate: {rate:.1f} Hz, Last value: {value}")
                else:
                    errors += 1
            except Exception as e:
                errors += 1
                
except KeyboardInterrupt:
    print("\n⚠ Interrupted by user")

finally:
    ser.close()

# Results
print("\n5. Results:")
print("-" * 40)

if len(samples) > 0:
    print(f"✓ Total samples received: {len(samples)}")
    print(f"✓ Sampling rate: {len(samples)/10:.1f} Hz")
    print(f"✓ Value range: {min(samples)} - {max(samples)}")
    print(f"✓ Average value: {sum(samples)/len(samples):.1f}")
    
    if errors > 0:
        print(f"⚠ Errors encountered: {errors}")
    
    # Check sampling rate
    expected_rate = 250
    actual_rate = len(samples) / 10
    
    if actual_rate < expected_rate * 0.8:
        print(f"\n⚠ WARNING: Sampling rate is low!")
        print(f"   Expected: ~{expected_rate} Hz")
        print(f"   Actual: {actual_rate:.1f} Hz")
        print("   Possible causes:")
        print("   - Arduino sketch delay is too long")
        print("   - Serial buffer overflow")
        print("   - USB connection issues")
    else:
        print(f"\n✓ Sampling rate is good ({actual_rate:.1f} Hz)")
    
    # Check value range
    if max(samples) <= 100 or max(samples) >= 4000:
        print(f"\n⚠ WARNING: Unusual ADC values!")
        print(f"   Expected range: 100-4000")
        print(f"   Actual range: {min(samples)}-{max(samples)}")
        print("   Possible causes:")
        print("   - Sensor not connected properly")
        print("   - Wrong voltage reference")
        print("   - Sensor malfunction")
    else:
        print(f"\n✓ ADC values look reasonable")
    
    print("\n6. Diagnosis:")
    print("-" * 40)
    if len(samples) > 2000 and actual_rate > 200 and 100 < max(samples) < 4000:
        print("✅ ALL TESTS PASSED!")
        print("   Your Arduino connection is working properly.")
        print("   The web application should work fine.")
    else:
        print("⚠ SOME ISSUES DETECTED")
        print("   Review warnings above and fix issues.")
        print("   Then try the web application again.")
    
else:
    print("❌ NO DATA RECEIVED!")
    print("\nPossible causes:")
    print("1. Arduino sketch not uploaded")
    print("   - Open Arduino IDE")
    print("   - Upload arduino_eeg_sketch.ino")
    print("   - Verify upload was successful")
    print("")
    print("2. Wrong baud rate")
    print("   - Check sketch uses Serial.begin(115200)")
    print("   - This script uses 115200 baud")
    print("")
    print("3. Arduino not sending data")
    print("   - Open Arduino Serial Monitor")
    print("   - Set to 115200 baud")
    print("   - Should see numbers scrolling")
    print("   - If not, check sketch and sensor")
    print("")
    print("4. Hardware issue")
    print("   - Check USB cable (must be data cable, not power-only)")
    print("   - Try different USB port")
    print("   - Check Arduino has power (LED on)")

print("\n" + "="*60)
print("Diagnostic complete. Press Enter to exit.")
input()