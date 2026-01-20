import serial
import numpy as np
import matplotlib.pyplot as plt
import time

# ---------------- USER SETTINGS ----------------
PORT = 'COM6'          # 🔴 Change this to your Arduino COM port
BAUD_RATE = 115200
ADC_MAX = 4095         # Arduino UNO R4 = 12-bit ADC
VREF = 3.3             # BioAmp EXG Pill uses 3.3V
WINDOW_SIZE = 500      # Samples to display (~2 sec @ 250 Hz)
# -----------------------------------------------

# Open serial connection
ser = serial.Serial(PORT, BAUD_RATE)
time.sleep(2)  # Allow Arduino reset

data_buffer = np.zeros(WINDOW_SIZE)

plt.ion()
fig, ax = plt.subplots()
line, = ax.plot(data_buffer)
ax.set_title("Raw EEG Signal (BioAmp EXG Pill)")
ax.set_xlabel("Samples")
ax.set_ylabel("Voltage (V)")
ax.set_ylim(0, VREF)

print("Started EEG streaming... Blink your eyes to test.")

while True:
    try:
        if ser.in_waiting:
            raw = ser.readline().decode().strip()

            if raw.isdigit():
                adc_value = int(raw)
                voltage = (adc_value / ADC_MAX) * VREF

                data_buffer = np.roll(data_buffer, -1)
                data_buffer[-1] = voltage

                line.set_ydata(data_buffer)
                plt.pause(0.001)

    except KeyboardInterrupt:
        print("\nStopped by user")
        break

ser.close()
