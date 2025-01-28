"""
Purpose:
    Print statistics presented in the paper.

Inputs:
    None

Outputs:
    None. Outputs are printed. To record the output, run the following:
        python print_stats.py >> output_file.txt

Author:
    Matthew R. DeVerna
"""

import os
import sys

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT_DIR = "../figures"
CURR_DIR = "stats_scripts"
RESULTS_DIR = "../sim_results/effects_of_lambda"
MAX_LAMBDA = 3.0

# Ensure we are in the data_analysis directory for paths to work
if os.path.basename(os.getcwd()) != CURR_DIR:
    raise Exception(f"Must run this script from the `{CURR_DIR}` directory!")

# Load simulation source code
source_dir = "../src"
sys.path.insert(0, source_dir)
from simulations import get_peak_day

print("-" * 75)
print("Statistics utilized in the paper")
print("-" * 75)
print("\n")

### Load simulation results ###
totals_df = pd.read_csv(os.path.join(RESULTS_DIR, "total_infected_all_settings.csv"))
by_day_df = pd.read_csv(os.path.join(RESULTS_DIR, "daily_infected_all_settings.csv"))

## Select the data we want ##
# ------------------------- #

# Total infections
lambda_3 = totals_df[
    (totals_df["beta"] == 0.3)
    & (totals_df["frac_mis"] == 0.5)
    & (totals_df["lambda"] == 3)
]

# By day for each lambda value
by_day_lambda_3 = by_day_df[
    (by_day_df["lambda"] == 3)
    & (by_day_df["beta"] == 0.3)
    & (by_day_df["frac_ord"] == 0.5)
]

by_day_lambda_1 = by_day_df[
    (by_day_df["lambda"] == 1)
    & (by_day_df["beta"] == 0.3)
    & (by_day_df["frac_ord"] == 0.5)
]

# Select/calculate the values we want to print
mis_vs_ord_diff = lambda_3["diff"].values[0]  # Misinformed - Ordinary
mis_vs_ord_extra = lambda_3["extra_inf"].values[0]  # Total lambda 3 - total lambda = 1

peak_day_mis = get_peak_day(by_day_lambda_3["infections_mis"])
peak_day_ord = get_peak_day(by_day_lambda_3["infections_ord"])

peak_day_lambda_1 = get_peak_day(by_day_lambda_1["infections_total"])
peak_day_lambda_3 = get_peak_day(by_day_lambda_3["infections_total"])
diff = peak_day_lambda_1 - peak_day_lambda_3


print("VARYING LAMBDA")
print("-" * 50)
print(
    f"Total extra infections incurred by misinformed group (vs. ordinary):{mis_vs_ord_diff:.1%}"
)
print(
    f"Total extra infections incurred by network (lambda 1 vs lambda 3.0): {mis_vs_ord_extra:.1%}"
)

print(f"Peak day for misinformed group: {peak_day_mis} (lambda = 3.0)")
print(f"Peak day for ordinary group: {peak_day_ord} (lambda = 3.0)")

print(f"Network peak (misinformed + ordinary), lambda 1: {peak_day_lambda_1} days")
print(f"Network peak (misinformed + ordinary), lambda 3: {peak_day_lambda_3} days")
print(f"Network peak (misinformed + ordinary), difference:: {diff} days")
