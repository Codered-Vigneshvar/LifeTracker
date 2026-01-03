#!/bin/bash
# Use absolute paths for robustness
PROJECT_DIR="/Users/vigneshvars/Documents/Tracker"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
APP_SCRIPT="$PROJECT_DIR/app.py"

cd "$PROJECT_DIR" || exit 1

# Execute Streamlit using the virtualenv python directly
"$VENV_PYTHON" -m streamlit run "$APP_SCRIPT" --server.port 8501 --server.headless true
