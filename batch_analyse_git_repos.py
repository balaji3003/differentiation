import os
import subprocess

# === CONFIGURATION ===
REPO_URLS = [
    "https://github.com/Neamar/KISS.git",
    "https://github.com/federicoiosue/Omni-Notes.git",
    "https://github.com/k9mail/k-9.git"
]

BASE_DIR = os.path.expanduser("~/Desktop/test_research")
SCRIPT_DIR = os.path.join(BASE_DIR, "scripts")

COMPLEXITY_SCRIPT = "analyse_cyclomatic_complexity_over_time.py"
TEST_ADOPTION_SCRIPT = "detect_test_adoption.py"
PLOT_SCRIPT = "plot_cyclomatic_complexity_timeseries.py"

def run_script(script_name, cwd, pass_repo_path=False):
    script_path = os.path.join(SCRIPT_DIR, script_name)
    print(f"⚙️ Running {script_name} on {os.path.basename(cwd)}...")
    if pass_repo_path:
        subprocess.run(["python3", script_path, cwd], cwd=SCRIPT_DIR)
    else:
        subprocess.run(["python3", script_path], cwd=cwd)

def safe_repo_name(url):
    return os.path.splitext(os.path.basename(url.rstrip("/")))[0]

# === MAIN EXECUTION ===
os.makedirs(BASE_DIR, exist_ok=True)

for repo_url in REPO_URLS:
    repo_name = safe_repo_name(repo_url)
    repo_path = os.path.join(BASE_DIR, repo_name)

    if not os.path.exists(repo_path):
        print(f"\n🌐 Cloning {repo_url} into {repo_path}...")
        subprocess.run(["git", "clone", repo_url, repo_path])
    else:
        print(f"\n📁 Repository already exists: {repo_name}")

    print(f"\n🚀 Analyzing repository: {repo_name}")

    # Run complexity script with repo path as an argument
    run_script(COMPLEXITY_SCRIPT, repo_path, pass_repo_path=True)

    # Run test adoption and plot scripts normally (they operate in-place)
    run_script(TEST_ADOPTION_SCRIPT, repo_path)
    run_script(PLOT_SCRIPT, repo_path)

    print(f"✅ Done: {repo_name}")

print("\n🎉 All repositories processed successfully.")
