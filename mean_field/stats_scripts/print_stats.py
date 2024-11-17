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
totals_df = pd.read_csv(os.path.join(RESULTS_DIR, "total_infected.csv"))
by_day_df = pd.read_csv(os.path.join(RESULTS_DIR, "daily_infected.csv"))

print("VARYING LAMBDA")
print("-" * 50)
total_max_only = totals_df.loc[np.isclose(totals_df["lambda"], MAX_LAMBDA)]
print(
    f"Total extra infections incurred by misinformed group (vs. ordinary): {total_max_only['diff'].max() : .1%}"
)
print(
    f"Total extra infections incurred by network (lambda 1 vs lambda {MAX_LAMBDA}): {total_max_only['total_extra'].max() : .1%}"
)
for group in ["misinformed", "ordinary"]:
    temp_slice = by_day_df[
        (np.isclose(by_day_df["lambda"], MAX_LAMBDA)) & (by_day_df["group"] == group)
    ]

    peak_day = get_peak_day(temp_slice["value"])
    print(f"Peak day for {group} group: {peak_day} (lambda = {MAX_LAMBDA})")

# 'combined' here means "the entire network"
combined_by_day = by_day_df[by_day_df["group"] == "combined"].reset_index(drop=True)
combined_max_lambda = combined_by_day[combined_by_day["lambda"] == MAX_LAMBDA]
comb_lambda1 = combined_by_day[combined_by_day["lambda"] == 1]

comb_max_lambda_peak_day = get_peak_day(combined_max_lambda["value"])
comb_lambda1_peak_day = get_peak_day(comb_lambda1["value"])

net_peak_str = "Network peak (misinformed + ordinary)"
print(f"{net_peak_str}, lambda = {MAX_LAMBDA}: {comb_max_lambda_peak_day} days")
print(f"{net_peak_str}, lambda = 1: {comb_lambda1_peak_day} days")
print(
    f"{net_peak_str}, difference: {comb_lambda1_peak_day - comb_max_lambda_peak_day} days"
)
