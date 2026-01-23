import serial
import time
import csv
import os

# ---------------- SETTINGS ----------------
PORT = "COM6"          # 🔴 change if needed
BAUD = 115200
DURATION_SEC = 300     # 5 minutes per session
SAVE_PATH = "../data/calibration/"
# -----------------------------------------

os.makedirs(SAVE_PATH, exist_ok=True)

# -------- ASK USER --------
session = input("Enter session name (calm / not_calm): ").strip().lower()
filename = SAVE_PATH + f"{session}_raw.csv"

# -------- SERIAL --------
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

print(f"\nRecording '{session}' session for {DURATION_SEC} seconds...")
print("Press CTRL+C to stop early.\n")

start_time = time.time()

with open(filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Time(s)", "ADC"])

    try:
        while time.time() - start_time < DURATION_SEC:
            if ser.in_waiting:
                raw = ser.readline().decode(errors="ignore").strip()
                if raw.isdigit():
                    t = time.time() - start_time
                    writer.writerow([f"{t:.4f}", int(raw)])
    except KeyboardInterrupt:
        print("\nRecording stopped early by user.")

ser.close()
print(f"\nData saved to: {filename}")
