import pandas as pd
import os

# ---------------- PATHS ----------------
INPUT_PATH = "../data/pipeline_output/"
OUTPUT_PATH = "../data/module8_ai/"
# --------------------------------------

os.makedirs(OUTPUT_PATH, exist_ok=True)

# Load feature files
calm = pd.read_csv(INPUT_PATH + "calm_features.csv")
not_calm = pd.read_csv(INPUT_PATH + "not_calm_features.csv")

# Add labels
calm["Label"] = "Calm"
not_calm["Label"] = "Not Calm"

# Combine
data = pd.concat([calm, not_calm], ignore_index=True)

# Select final columns
final_df = data[["Alpha", "Beta", "AlphaBetaRatio", "Label"]]

# Shuffle (important)
final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save
final_df.to_csv(
    OUTPUT_PATH + "features_labels_v3.csv",
    index=False
)

print("Training dataset created:")
print(OUTPUT_PATH + "features_labels_v3.csv")
print("\nLabel distribution:")
print(final_df["Label"].value_counts())
