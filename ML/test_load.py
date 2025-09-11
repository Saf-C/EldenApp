import pandas as pd

raw_df = pd.read_csv("../ml_presets_V5.6.csv")          # go up one level into project root
ready_df = pd.read_csv("../ml_presets_ready_V5.5.csv")

print("Raw dataset:")
print(raw_df.head())

print("\nReady dataset:")
print(ready_df.head())
