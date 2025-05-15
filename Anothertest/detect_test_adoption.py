import subprocess
import os
import re
from collections import defaultdict
from datetime import datetime

LOG_LINES = []

def log(msg):
    print(msg)
    LOG_LINES.append(msg)

def run_git_command(cmd):
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return result.stdout.decode("utf-8").strip()

def get_first_addition_of_ci_configs():
    log("\n🔍 Searching for CI configuration introduction...")
    ci_keywords = ['.github/workflows', '.travis.yml', '.circleci', '.gitlab-ci.yml']
    log_data = run_git_command("git log --diff-filter=A --name-only --pretty=format:'%h|%ad|%an|%s' --date=short")
    for line in log_data.splitlines():
        for keyword in ci_keywords:
            if keyword in line:
                log(f"✅ CI config added: {line}")
                return line.split('|')[0]
    log("❌ No CI configuration file detected.")
    return None

def get_first_test_dir_creation():
    log("\n🔍 Searching for test directory introduction...")
    log_data = run_git_command("git log --diff-filter=A --name-only --pretty=format:'%h|%ad|%an|%s' --date=short")
    for line in log_data.splitlines():
        if re.search(r'(^|/)test/|src/test|__tests__', line):
            log(f"✅ Test directory/file added: {line}")
            return line.split('|')[0]
    log("❌ No test directory creation detected.")
    return None

def detect_test_commit_spikes():
    log("\n📈 Detecting spike in test-related commits...")
    log_data = run_git_command("git log --all --since='5 years ago' --pretty=format:'%ad %s' --date=short")
    monthly_count = defaultdict(int)
    for line in log_data.splitlines():
        if 'test' in line.lower():
            try:
                date = line.split()[0]
                month = '-'.join(date.split('-')[:2])
                monthly_count[month] += 1
            except:
                continue
    if not monthly_count:
        log("❌ No test-related commit spikes detected.")
        return
    for month, count in sorted(monthly_count.items(), key=lambda x: -x[1])[:5]:
        log(f"📅 {month}: {count} test-related commits")

def check_coverage_badge():
    log("\n🛡️ Checking README for coverage badge...")
    readme_files = ['README.md', 'README.rst', 'readme.md']
    for file in readme_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
                if 'coverage' in content:
                    log(f"✅ Coverage reference found in {file}")
                    log("🔍 Searching git history for when it was introduced...")
                    log_data = run_git_command(f"git log -p {file}")
                    matches = re.findall(r'^commit\s+([a-f0-9]{7,})', log_data, re.MULTILINE)
                    if matches:
                        log(f"📜 Potential commit introducing coverage badge: {matches[0]}")
                        return matches[0]
    log("❌ No coverage badge or reference found in README.")
    return None

def save_output_to_file():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_filename = f"output_test_adoption_{timestamp}.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(LOG_LINES))
    print(f"\n📁 Results saved to: {output_filename}")

def main():
    log(f"📦 Analyzing Repository: {os.path.basename(os.getcwd())}")

    ci_commit = get_first_addition_of_ci_configs()
    test_commit = get_first_test_dir_creation()
    detect_test_commit_spikes()
    coverage_commit = check_coverage_badge()

    log("\n📌 Summary of Commit Hashes:")
    log(f"   - CI Config Added: {ci_commit or '❌ Not found'}")
    log(f"   - Test Dir Created: {test_commit or '❌ Not found'}")
    log(f"   - Coverage Badge Added: {coverage_commit or '❌ Not found'}")

    save_output_to_file()

if __name__ == "__main__":
    main()
