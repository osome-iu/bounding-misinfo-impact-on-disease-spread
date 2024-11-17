#!/bin/bash

# Submit SLURM batch scripts located in subdirectories of sir_scripts.
# ----------------------------------------------------------------
# This script iterates over subdirectories inside sir_scripts and
# submits each SLURM batch script found within those subdirectories.

# MUST UPDATE WITH ABSOLUTE PATH FOR YOUR SYSTEM.
CURR_DIR="/N/slate/mdeverna/bounding-misinfo-impact-on-disease-spread/abm/code"

# Check if the current working directory is not CURR_DIR
if [[ "$(pwd)" != "$CURR_DIR" ]]; then
    echo "Error: This script must be run from the $CURR_DIR directory."
    exit 1
fi

# MUST UPDATE WITH ABSOLUTE PATH FOR YOUR SYSTEM.
SIR_SCRIPTS_DIR="/N/slate/mdeverna/bounding-misinfo-impact-on-disease-spread/abm/code/sir_scripts"

# Check if the sir_scripts directory exists
if [ ! -d "$SIR_SCRIPTS_DIR" ]; then
    echo "Error: Directory $SIR_SCRIPTS_DIR does not exist."
    exit 1
fi

# Iterate over each subdirectory in sir_scripts
for lt_dir in "$SIR_SCRIPTS_DIR"/*; do

    # Check if it is a directory and not the README file
    if [ -d "$lt_dir" ]; then
        echo "Entering directory $lt_dir..."

        # Iterate over each script file in the subdirectory
        for script_file in "$lt_dir"/*.script; do

            # Check if the file exists
            if [ -f "$script_file" ]; then
                echo "Submitting $script_file to SLURM scheduler..."
                sbatch "$script_file"
            fi
        done
    fi
done

echo "All SIR simulation scripts have been submitted to SLURM."
