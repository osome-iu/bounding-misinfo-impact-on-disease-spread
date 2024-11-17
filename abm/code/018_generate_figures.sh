#!/bin/bash

# Generate all figures.
# ----------------------------------------------------------------
# Runs all scripts in plotting_scripts that generate figures.
#
# Author: Matthew DeVerna

# MUST UPDATE WITH ABSOLUTE PATH FOR YOUR SYSTEM.
CURR_DIR="/Users/mdeverna/Documents/Projects/bounding-misinfo-impact-on-disease-spread/abm/code"

# Check if the current working directory is not CURR_DIR
if [[ "$(pwd)" != "$CURR_DIR" ]]; then
    echo "Error: This script must be run from the $CURR_DIR directory."
    exit 1
fi

echo "GENERATING FIGURES..."
echo ""

echo "Running 001_effect_of_misinformed_on_infections.py ..."
python plotting_scripts/001_effect_of_misinformed_on_infections.py 

echo "Running 002_density_robustness.py ..."
python plotting_scripts/002_density_robustness.py 

echo "Running 003_sampling_robustness.py ..."
python plotting_scripts/003_sampling_robustness.py 

echo ""
echo "All figures have been generated."