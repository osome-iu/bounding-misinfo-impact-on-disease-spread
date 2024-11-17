"""
Purpose:
    Simulate the effects of varying tau, recovery period in days. The misinformed
        population and homophily are not considered here.

Inputs:
    None

Outputs:
    Output Directory: sim_results/effects_of_tau
    - r0s.csv : the R_0 value given a particular beta
    - daily_infections.csv : proportion of the network infected by day
    - peak_days.csv : the peak day of infection for each recovery period

Author:
    Matthew R. DeVerna
"""

import os
import sys

import numpy as np
import pandas as pd

OUT_DIR = "../sim_results"
SUB_DIR = "effects_of_tau"
CURR_DIR = "sim_scripts"
# Ensure we are in the data_analysis directory for paths to work
if os.path.basename(os.getcwd()) != CURR_DIR:
    raise Exception(f"Must run this script from the `{CURR_DIR}` directory!")

# Load simulation source code
source_dir = "../src"
sys.path.insert(0, source_dir)
from simulations import run_simulation, get_peak_day


### SET SIMULATION PARAMETERS ###
frac_ord = 1  # No misinformed for initial simulations
prop_infected = 0.001
num_days = 100
recovery_days = 5  # recovery rate gamma = .2 where recovery days = 1/.2 = 5
beta_mult = 1  # this doesn't really matter here
homophily = False  # not tested here
alpha = None  # full mixing (homophily tested later)

# Will store the progression of infections over time, indexed by beta values
# Storage
r0_records = []
peak_records = []
daily_infection_records = []

# We fix beta at .3 based on the above
beta = 0.3

# Simulate across various recovery periods
recovery_days = np.arange(1, 21, 1)
for rec_days in recovery_days:
    # Run the simulation based on the input
    S_o, S_m, I_o, I_m, R_o, R_m, r0s = run_simulation(
        frac_ord=frac_ord,
        prop_infec=prop_infected,
        num_days=num_days,
        beta_ord=beta,
        recovery_days=rec_days,
        beta_mult=beta_mult,
        w_homophily=homophily,
        alpha=None,
        mixed=True,
    )

    # Below r0s = (r0_ord, r0_mis, r0_weighted)
    # All are identical in this simulation
    r0_records.append({"recovery": rec_days, "r0": r0s[0]})
    peak_records.append({"recovery": rec_days, "peak_day": get_peak_day(I_o)})

    for day, prop in enumerate(I_o):
        daily_infection_records.append(
            {"recovery": rec_days, "day": day, "prop_infected": prop}
        )

# Convert to dfs
r0_df = pd.DataFrame.from_records(r0_records)
daily_infection_df = pd.DataFrame.from_records(daily_infection_records)
peak_day_df = pd.DataFrame.from_records(peak_records)

### Save results ###
out_dir = os.path.join(OUT_DIR, SUB_DIR)
os.makedirs(out_dir, exist_ok=True)
r0_df.to_csv(os.path.join(out_dir, "r0s.csv"), index=False)
daily_infection_df.to_csv(os.path.join(out_dir, "daily_infections.csv"), index=False)
peak_day_df.to_csv(os.path.join(out_dir, "peak_days.csv"), index=False)
