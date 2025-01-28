#!/bin/bash

# Purpose:
#   Run the entire ABM pipeline. See individual scripts for details.
#
# Inputs:
#   None
#
# Output:
#   See individual scripts for information about their respective outputs.
#
# How to call:
#   ```
#   bash run_pipeline.sh
#   ```
#
# Author: Matthew DeVerna

# Throw error if not in correct directory
EXPECTED_DIR="mean_field"
CURRENT_DIR=$(basename "$PWD")

if [ "$CURRENT_DIR" != "$EXPECTED_DIR" ]; then
  echo "Error: This script must be run from the $EXPECTED_DIR directory."
  exit 1  # Exit with an error code of 1
fi

### Run all simulation scripts ###
# ------------------------------ #
cd sim_scripts

echo "##########################################"
echo "--------- Running ABM Simulations --------"
echo "##########################################"
echo ""
echo ""

echo "Running simulate_effects_of_beta.py ..."; python3 simulate_effects_of_beta.py
echo "Running simulate_effects_of_rec_period.py ..."; python3 simulate_effects_of_rec_period.py
echo "Running simulate_effects_of_lambda_all_settings.py ..."; python3 simulate_effects_of_lambda_all_settings.py
echo "Running simulate_effects_of_homophily.py ..."; python3 simulate_effects_of_homophily.py
echo "Running simulate_homophily_on_misinformed.py ..."; python3 simulate_homophily_on_misinformed.py

### Generate all figures ###
# ------------------------ #
cd ../figures_generation

echo ""
echo "##########################################"
echo "----------- Generating Figures -----------"
echo "##########################################"
echo ""
echo ""

echo "Running generate_beta_figure.py ..."; python3 generate_beta_figure.py
echo "Running generate_tau_figure.py ..."; python3 generate_tau_figure.py
echo "Running generate_lambda_figure.py ..."; python3 generate_lambda_figure.py
echo "Running generate_misinformed_prop_size_figure.py ..."; python3 generate_misinformed_prop_size_figure.py
echo "Running generate_homophily_figure.py ..."; python3 generate_homophily_figure.py
echo "Running generate_homophily_on_misinformed_figure_3d.py ..."; python3 generate_homophily_on_misinformed_figure_3d.py

### Run stats file ###
# ------------------------ #
cd ../stats_scripts

echo ""
echo "##########################################"
echo "------------ Generating Stats ------------"
echo "##########################################"
echo ""
echo ""

echo "Creating stats_results directory ..."; mkdir ../stats_results
echo "Running print_stats.py ..."; python3 print_stats.py > ../stats_results/stats.txt

echo ""
echo "##########################################"
echo "----------- Pipeline Completed -----------"
echo "##########################################"
