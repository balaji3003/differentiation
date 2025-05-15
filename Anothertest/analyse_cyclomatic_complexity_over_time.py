import os
import subprocess
import pandas as pd
from datetime import datetime

# === CONFIGURATION ===
REPO_DIR = "."  # Run from the root of the repo
REPO_NAME = os.path.basename(os.path.abspath(REPO_DIR))
INTERVAL = '4 weeks'  # Granularity of commit sampling
OUTPUT_CSV = f"{REPO_NAME}_cyclomatic_complexity_over_time.csv"
MAX_COMMITS = 100  # Max commits to analyze (can increase for deeper history)

# === HELPER FUNCTIONS ===
def run_cmd(cmd, cwd=REPO_DIR):
    result = subprocess.run(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode("utf-8").strip()

def get_sampled_commits(limit=100):
    print(f"📦 Sampling commits at ~{INTERVAL} intervals (limit {limit})...")
    cmd = "git log --date=short --reverse --pretty=format:'%H|%ad'"
    lines = run_cmd(cmd).splitlines()
    sampled = []
    seen_months = set()

    for line in lines:
        if "|" not in line: continue
        sha, date = line.split("|")
        month = date[:7]
        if month not in seen_months:
            sampled.append((sha, date))
            seen_months.add(month)
        if len(sampled) >= limit:
            break
    return sampled

def checkout_commit(commit_hash):
    print(f"🔁 Checking out commit {commit_hash}...")
    run_cmd(f"git checkout {commit_hash}")


def analyze_lizard_complexity():
    output = run_cmd("lizard -l java .")
    complexities = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 6 and parts[0].isdigit():
            try:
                complexities.append(int(parts[0]))
            except ValueError:
                continue
    total = sum(complexities)
    count = len(complexities)
    average = total / count if count > 0 else 0
    return total, count, average

# === MAIN LOGIC ===
def analyze_cyclomatic_complexity_over_time():
    commits = get_sampled_commits(MAX_COMMITS)
    results = []

    print(f"🔁 Analyzing {len(commits)} commits...\n")

    for idx, (commit, date) in enumerate(commits):
        print(f"[{idx + 1}/{len(commits)}] Commit: {commit} Date: {date}")
        checkout_commit(commit)
        total, functions, avg = analyze_lizard_complexity()
        results.append({
            "commit": commit,
            "date": date,
            "total_complexity": total,
            "function_count": functions,
            "average_complexity": round(avg, 2)
        })

    # Export to CSV
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ Cyclomatic complexity history saved to: {OUTPUT_CSV}")

# === ENTRY POINT ===
if __name__ == "__main__":
    analyze_cyclomatic_complexity_over_time()
