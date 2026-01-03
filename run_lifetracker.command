#!/bin/bash
# Double-click to start LifeTracker
cd "$(dirname "$0")"
echo "Starting LifeTracker..."
./venv/bin/streamlit run app.py --server.port 8501
