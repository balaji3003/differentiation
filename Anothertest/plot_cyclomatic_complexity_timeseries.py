import pandas as pd
import matplotlib.pyplot as plt
import os

# === CONFIGURATION ===
REPO_NAME = os.path.basename(os.path.abspath("."))
CSV_FILE = f"{REPO_NAME}_cyclomatic_complexity_over_time.csv"
PLOT_FILE = f"{REPO_NAME}_cyclomatic_complexity_timeseries.png"

# === LOAD DATA ===
if not os.path.exists(CSV_FILE):
    raise FileNotFoundError(f"CSV file '{CSV_FILE}' not found.")

df = pd.read_csv(CSV_FILE, parse_dates=['date'])
df.sort_values('date', inplace=True)

# === PLOT AVERAGE COMPLEXITY ===
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['average_complexity'], marker='o', label='Average Complexity per Function')
plt.title(f"Cyclomatic Complexity Over Time: {REPO_NAME}")
plt.xlabel("Commit Date")
plt.ylabel("Average Cyclomatic Complexity")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.legend()

# === SAVE ONLY ===
plt.savefig(PLOT_FILE)
print(f"✅ Plot saved to {PLOT_FILE}")
