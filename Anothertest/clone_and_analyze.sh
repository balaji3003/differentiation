#!/bin/bash

# === FULL LIST OF TARGET REPOS ===
REPO_LIST=(
  "https://github.com/k9mail/k-9.git"
  "https://github.com/TeamNewPipe/NewPipe.git"
  "https://github.com/federicoiosue/Omni-Notes.git"
  "https://github.com/Neamar/KISS.git"
  "https://github.com/fossasia/open-event-android.git"
  "https://github.com/raulhaag/MiMangaNu.git"
  "https://github.com/genonbeta/TrebleShot.git"
)

# === PATHS ===
WORK_DIR="$HOME/Desktop/test_research/Anothertest/workspace"
SCRIPT_DIR="$HOME/Desktop/test_research/Anothertest"
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

REQUIRED_PYTHON_PACKAGES=("pandas" "matplotlib")
REQUIRED_SYSTEM_TOOLS=("git" "python3" "pip3" "lizard")

# === STEP 0: CHECK REQUIREMENTS ===
echo "🔍 Checking required system tools..."
for tool in "${REQUIRED_SYSTEM_TOOLS[@]}"; do
    if ! command -v $tool &> /dev/null; then
        echo "❌ Required tool '$tool' is not installed. Please install it and try again."
        exit 1
    fi
done

echo "✅ All required tools found."

echo "📦 Ensuring Python packages are installed..."
for pkg in "${REQUIRED_PYTHON_PACKAGES[@]}"; do
    if ! python3 -c "import $pkg" &> /dev/null; then
        echo "➕ Installing missing package: $pkg"
        pip3 install --user $pkg
    else
        echo "✅ Package '$pkg' is already installed."
    fi
done

if ! command -v lizard &> /dev/null; then
    echo "➕ Installing 'lizard'..."
    pip3 install --user lizard
else
    echo "✅ 'lizard' is already installed."
fi

# === STEP 1: PREPARE WORKSPACE ===
mkdir -p "$WORK_DIR"
cd "$WORK_DIR" || exit 1

# === STEP 2: PROCESS EACH REPO ===
for REPO_URL in "${REPO_LIST[@]}"; do
    REPO_NAME=$(basename -s .git "$REPO_URL")
    REPO_DIR="$WORK_DIR/$REPO_NAME"
    LOG_FILE="$LOG_DIR/${REPO_NAME}_log.txt"
    PLOT_FILE="${REPO_NAME}_cyclomatic_complexity_timeseries.png"

    {
        echo ""
        echo "🌐 Cloning or updating $REPO_NAME..."
        if [ -d "$REPO_DIR/.git" ]; then
            (cd "$REPO_DIR" && git pull)
        else
            git clone "$REPO_URL" "$REPO_DIR"
        fi

        echo "📁 Copying .py scripts into $REPO_NAME..."
        cp "$SCRIPT_DIR"/*.py "$REPO_DIR/"

        echo "🚀 Running detect_test_adoption.py..."
        (cd "$REPO_DIR" && python3 detect_test_adoption.py)

        echo "🚀 Running analyse_cyclomatic_complexity_over_time.py..."
        (cd "$REPO_DIR" && python3 analyse_cyclomatic_complexity_over_time.py)

        echo "🚀 Running plot_cyclomatic_complexity_timeseries.py..."
        (cd "$REPO_DIR" && python3 plot_cyclomatic_complexity_timeseries.py)

        # Copy PNG to logs folder
        if [ -f "$REPO_DIR/$PLOT_FILE" ]; then
            cp "$REPO_DIR/$PLOT_FILE" "$LOG_DIR/"
            echo "📊 Plot copied to $LOG_DIR/$PLOT_FILE"
        else
            echo "⚠️  Plot file not found: $PLOT_FILE"
        fi

        echo "✅ Finished all steps for $REPO_NAME"
        echo "---------------------------------------------"
    } | tee "$LOG_FILE"
done

echo ""
echo "🎉 All repositories processed. Logs and plots saved to: $LOG_DIR"
