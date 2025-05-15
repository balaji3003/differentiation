import pandas as pd
import matplotlib.pyplot as plt
import os

# === CONFIGURATION ===
REPO_NAME = os.path.basename(os.path.abspath("."))
RESULT_DIR = os.path.expanduser(f"~/Desktop/test_research/results/{REPO_NAME}")
CSV_FILE = os.path.join(RESULT_DIR, f"{REPO_NAME}_cyclomatic_complexity_over_time.csv")
PLOT_FILE = os.path.join(RESULT_DIR, f"{REPO_NAME}_cyclomatic_complexity_timeseries.png")

# === LOAD DATA ===
if not os.path.exists(CSV_FILE):
    raise FileNotFoundError(f"CSV file '{CSV_FILE}' not found in {RESULT_DIR}.")

df = pd.read_csv(CSV_FILE, parse_dates=['date'])
df.sort_values('date', inplace=True)

# === PLOT ===
os.makedirs(RESULT_DIR, exist_ok=True)
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['average_complexity'], marker='o', label='Average Complexity per Function')
plt.title(f"Cyclomatic Complexity Over Time: {REPO_NAME}")
plt.xlabel("Commit Date")
plt.ylabel("Average Cyclomatic Complexity")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.legend()
plt.savefig(PLOT_FILE)
plt.show()

print(f"✅ Plot saved to {PLOT_FILE}")
