import pandas as pd
import json

# Load JSON file
with open("./output/data/shuffled_raw.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert JSON to DataFrame
df = pd.DataFrame(data)

# Rename columns
df = df.rename(columns={"target": "label", "func": "message"})

# Keep only necessary columns
df = df[["label", "message"]]

# Save as tab-separated file
df.to_csv("formatted_dataset.tsv", sep="\t", index=False, header=False)

print("Dataset saved as formatted_dataset.tsv")