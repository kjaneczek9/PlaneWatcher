#!/bin/bash

# Path to your Python script
PYTHON_SCRIPT="read_planes.py"

# Loop indefinitely
while true; do
    # Run the Python script
   venv/bin/python "$PYTHON_SCRIPT"
    
    # Wait for 3 seconds before running the script again
    sleep 5
done

