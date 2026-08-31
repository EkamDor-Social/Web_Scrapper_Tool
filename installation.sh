#!/bin/bash

echo "=========================================="
echo "  Instagram Scraper - Setup"
echo "=========================================="
echo

# ----------------------------------------
# 1. Detect Operating System
# ----------------------------------------
OS="$(uname -s)"

case "$OS" in
    Darwin*) MACHINE="Mac";;
    MINGW*|MSYS*|CYGWIN*) MACHINE="Windows";;
    Linux*) MACHINE="Linux";;
    *) MACHINE="Unknown";;
esac

echo "[INFO] Detected Operating System: $MACHINE"
echo

# ----------------------------------------
# 2. Find Python
# ----------------------------------------
if [ "$MACHINE" = "Windows" ]; then
    if command -v python >/dev/null 2>&1; then
        PY_CMD="python"
    elif command -v python3 >/dev/null 2>&1; then
        PY_CMD="python3"
    else
        echo "[ERROR] Python was not found."
        echo "[ERROR] Install Python 3.11 or newer and restart Git Bash."
        exit 1
    fi
else
    if command -v python3 >/dev/null 2>&1; then
        PY_CMD="python3"
    elif command -v python >/dev/null 2>&1; then
        PY_CMD="python"
    else
        echo "[ERROR] Python was not found."
        echo "[ERROR] Install Python 3.11 or newer and try again."
        exit 1
    fi
fi

echo "[INFO] Python:"
"$PY_CMD" --version
echo

# ----------------------------------------
# 3. Check Required Files
# ----------------------------------------
if [ ! -f "Web_scrapper.py" ]; then
    echo "[ERROR] Web_scrapper.py not found."
    echo "[ERROR] Run this script from the project folder."
    exit 1
fi

echo "[INFO] Project files found."
echo

# ----------------------------------------
# 4. Create Virtual Environment
# ----------------------------------------
VENV_DIR="venv_instagram"

if [ "$MACHINE" = "Windows" ]; then
    VENV_PYTHON="$VENV_DIR/Scripts/python.exe"
else
    VENV_PYTHON="$VENV_DIR/bin/python"
fi

if [ ! -f "$VENV_PYTHON" ]; then
    echo "[INFO] Creating virtual environment..."
    "$PY_CMD" -m venv "$VENV_DIR"

    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment."
        exit 1
    fi
else
    echo "[INFO] Virtual environment already exists."
fi

echo

# ----------------------------------------
# 5. Upgrade pip
# ----------------------------------------
echo "[INFO] Upgrading pip..."

"$VENV_PYTHON" -m pip install --upgrade pip

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to upgrade pip."
    exit 1
fi

echo

# ----------------------------------------
# 6. Install Dependencies
# ----------------------------------------
echo "=========================================="
echo "[INFO] Installing Dependencies"
echo "=========================================="

"$VENV_PYTHON" -m pip install \
    selenium \
    webdriver-manager \
    pandas \
    openpyxl \
    jupyter \
    jupyterlab \
    notebook \
    ipykernel

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies."
    exit 1
fi

echo

# ----------------------------------------
# 7. Verify Installation
# ----------------------------------------
echo "=========================================="
echo "[INFO] Verifying Installation"
echo "=========================================="

"$VENV_PYTHON" -c "import selenium; print('OK - Selenium', selenium.__version__)"
"$VENV_PYTHON" -c "import pandas; print('OK - Pandas', pandas.__version__)"
"$VENV_PYTHON" -c "import jupyter; print('OK - Jupyter')"

if [ $? -ne 0 ]; then
    echo "[ERROR] Package verification failed."
    exit 1
fi

echo
echo "[INFO] Setup completed successfully."
echo

# ----------------------------------------
# 8. Start Scraper
# ----------------------------------------
echo "=========================================="
echo "[INFO] Starting Instagram Scraper"
echo "=========================================="
echo
echo "Press Ctrl+C to stop."
echo

"$VENV_PYTHON" Web_scrapper.py