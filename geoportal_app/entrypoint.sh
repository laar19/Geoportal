#!/bin/bash
set -e

echo "Running setup_db.py..."
python setup_db.py

echo "Starting Flask app..."
python main.py
