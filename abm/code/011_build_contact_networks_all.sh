#!/bin/bash

# Build all contact networks with SLURM in parallel.
# ----------------------------------------------------------------
# This script serves simply as a SLURM Batch Script executor, submitting
#  multiple SLURM batch scripts that are configured to generate
#  contact networks with different parameters.
#

# MUST UPDATE WITH ABSOLUTE PATH FOR YOUR SYSTEM.
CURR_DIR="/N/slate/mdeverna/bounding-misinfo-impact-on-disease-spread/abm/code"

# Directory containing the scripts
BUILD_SCRIPT_DIR="build_scripts"

# Check if the current working directory is not CURR_DIR
if [[ "$(pwd)" != "$CURR_DIR" ]]; then
    echo "Error: This script must be run from the $CURR_DIR directory."
    exit 1
fi

# Check if the directory exists
if [ ! -d "$BUILD_SCRIPT_DIR" ]; then
    echo "Error: Directory $BUILD_SCRIPT_DIR does not exist."
    exit 1
fi

# Loop through each .script file in the directory and submit it to the SLURM scheduler
for script_file in "$BUILD_SCRIPT_DIR"/*.script; do
    if [ -f "$script_file" ]; then
        echo "Submitting $script_file to SLURM scheduler..."
        sbatch "$script_file"
    fi
done

echo "All SLURM scripts have been submitted."
