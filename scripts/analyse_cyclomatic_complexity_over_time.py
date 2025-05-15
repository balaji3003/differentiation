import os
import subprocess
import pandas as pd
from datetime import datetime
import shlex
import sys

# === CONFIGURATION ===
REPO_DIR = sys.argv[1] if len(sys.argv) > 1 else "."  # Accept path from command line
REPO_NAME = os.path.basename(os.path.abspath(REPO_DIR))
INTERVAL = 'monthly'
MAX_COMMITS = 100
OUTPUT_DIR = os.path.expanduser(f"~/Desktop/test_research/results/{REPO_NAME}")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, f"{REPO_NAME}_cyclomatic_complexity_over_time.csv")


# === HELPER FUNCTIONS ===
def run_cmd(cmd, cwd=REPO_DIR):
    try:
        result = subprocess.run(shlex.split(cmd), cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return result.stdout.decode("utf-8").strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}\n{e.stderr.decode('utf-8')}")
        return ""

def get_sampled_commits(limit=100):
    print(f"📦 Sampling commits since last 10 years (~{INTERVAL} intervals)...")
    cmd = "git rev-list --since='10 years ago' --reverse --all --pretty=format:%H|%ad --date=short"
    lines = run_cmd(cmd).splitlines()
    sampled = []
    seen_months = set()

    for line in lines:
        if "|" not in line or len(line.split("|")[0]) != 40:
            continue
        sha, date = line.split("|")
        month = date[:7]
        if month not in seen_months:
            sampled.append((sha.strip(), date.strip()))
            seen_months.add(month)
        if len(sampled) >= limit:
            break

    print(f"✅ Collected {len(sampled)} commits.")
    return sampled

def checkout_commit(commit_hash):
    print(f"🔁 Checking out commit {commit_hash}...")
    run_cmd(f"git checkout {commit_hash}")

def get_lizard_complexity():
    java_files = []
    for root, dirs, files in os.walk(REPO_DIR):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))

    print(f"📁 Found {len(java_files)} .java files to analyze.")

    if not java_files:
        print("⚠️  No .java files found in this commit.")
        return 0, 0, 0

    file_list_path = os.path.join(REPO_DIR, "java_file_list.txt")
    with open(file_list_path, "w") as f:
        for path in java_files:
            f.write(f"{path}\n")

    output = run_cmd(f"lizard @{file_list_path}")
    os.remove(file_list_path)

    print("📤 Lizard raw output:")
    print(output)

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
    return total, count, round(average, 2)

# === MAIN LOGIC ===
def analyze_cyclomatic_complexity_over_time():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    original_branch = run_cmd("git rev-parse --abbrev-ref HEAD").strip()
    commits = get_sampled_commits(MAX_COMMITS)
    results = []

    print(f"\n🧪 Analyzing {len(commits)} commits...\n")

    for idx, (commit, date) in enumerate(commits):
        print(f"[{idx + 1}/{len(commits)}] Commit: {commit} Date: {date}")
        checkout_commit(commit)
        total, count, avg = get_lizard_complexity()
        results.append({
            "commit": commit,
            "date": date,
            "total_complexity": total,
            "function_count": count,
            "average_complexity": avg
        })

    print(f"\n🧹 Restoring original branch: {original_branch}")
    run_cmd(f"git checkout {original_branch}")

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ Cyclomatic complexity history saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    analyze_cyclomatic_complexity_over_time()
