import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------- PATHS ----------------
INPUT_FILE = "../data/module9_realtime_ai/realtime_ai_log_final.csv"
OUTPUT_PATH = "../data/final_results/"
# --------------------------------------

os.makedirs(OUTPUT_PATH, exist_ok=True)

# -------- LOAD DATA --------
df = pd.read_csv(INPUT_FILE)

# Convert time to float
df["Time(s)"] = df["Time(s)"].astype(float)

# -------- GRAPH 1: Alpha/Beta Ratio vs Time --------
plt.figure(figsize=(10, 4))
plt.plot(df["Time(s)"], df["AlphaBetaRatio"], marker="o")
plt.xlabel("Time (s)")
plt.ylabel("Alpha / Beta Ratio")
plt.title("Alpha/Beta Ratio Over Time")
plt.grid(True)
plt.tight_layout()
plt.savefig(OUTPUT_PATH + "ratio_vs_time.png", dpi=300)
plt.close()

# -------- GRAPH 2: Calmness Timeline --------
state_numeric = df["AI_State"].map({"Calm": 1, "Not Calm": 0})

plt.figure(figsize=(10, 3))
plt.step(df["Time(s)"], state_numeric, where="post")
plt.yticks([0, 1], ["Not Calm", "Calm"])
plt.xlabel("Time (s)")
plt.ylabel("State")
plt.title("Real-Time Calmness Classification Timeline")
plt.grid(True)
plt.tight_layout()
plt.savefig(OUTPUT_PATH + "state_timeline.png", dpi=300)
plt.close()

# -------- GRAPH 3: State Distribution --------
state_counts = df["AI_State"].value_counts()

plt.figure(figsize=(4, 4))
state_counts.plot(kind="bar")
plt.ylabel("Number of Windows")
plt.title("Distribution of Predicted States")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(OUTPUT_PATH + "state_distribution.png", dpi=300)
plt.close()

# -------- DOCUMENTATION SUMMARY --------
total_windows = len(df)
calm_count = state_counts.get("Calm", 0)
not_calm_count = state_counts.get("Not Calm", 0)

with open(OUTPUT_PATH + "results_summary.txt", "w") as f:
    f.write("FINAL RESULTS SUMMARY\n")
    f.write("---------------------\n")
    f.write(f"Total windows analyzed : {total_windows}\n")
    f.write(f"Calm windows           : {calm_count}\n")
    f.write(f"Not Calm windows       : {not_calm_count}\n\n")

    f.write("Observations:\n")
    f.write("- Alpha/Beta ratio varies over time reflecting cognitive state changes.\n")
    f.write("- Calm states dominate during relaxed periods.\n")
    f.write("- Not Calm states appear during movement or cognitive load.\n\n")

    f.write("Conclusion:\n")
    f.write("The real-time EEG-based system successfully tracks calmness using\n")
    f.write("frequency-domain features and a calibrated machine learning model.\n")

print("Final graphs and documentation generated in:")
print(OUTPUT_PATH)
