#!/bin/bash

# Get the app directory
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_DIR"

# Determine the project root directory (which contains the 'apps' folder)
PROJECT_ROOT_DIR="$(cd "$APP_DIR/../.." && pwd)"

# Set PYTHONPATH to include the project root directory
export PYTHONPATH=$PROJECT_ROOT_DIR

# Run the application with Python directly
python main.py 