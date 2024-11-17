"""
Purpose:
    Simulate the effects of varying beta (without misinformed population).

Inputs:
    None

Outputs:
    Output Directory: sim_results/effects_of_beta
    - r0s.csv : the R_0 value given a particular beta
    - daily_infections.csv : proportion of the network infected by day
    - cum_infections.csv : the cumulative proportion of the population infected
        at the end of the simulation

Author:
    Matthew R. DeVerna
"""

import os
import sys

import numpy as np
import pandas as pd

OUT_DIR = "../sim_results"
SUB_DIR = "effects_of_beta"
CURR_DIR = "sim_scripts"
# Ensure we are in the data_analysis directory for paths to work
if os.path.basename(os.getcwd()) != CURR_DIR:
    raise Exception(f"Must run this script from the `{CURR_DIR}` directory!")

# Load simulation source code
source_dir = "../src"
sys.path.insert(0, source_dir)
from simulations import run_simulation


### SET SIMULATION PARAMETERS ###
frac_ord = 1  # No misinformed for initial simulations
prop_infected = 0.001
num_days = 100
recovery_days = 5
beta_mult = 1  # This doesn't really matter here
homophily = False  # Not tested here
alpha = 0.5  # Full mixing (homophily tested later)

# Storage
r0_records = []
tot_prop_infected_records = []
daily_infection_records = []

# Simulations
beta_values = np.arange(0.02, 1.02, 0.02)
for beta in beta_values:
    S_o, S_m, I_o, I_m, R_o, R_m, r0s = run_simulation(
        frac_ord=frac_ord,
        prop_infec=prop_infected,
        num_days=num_days,
        beta_ord=beta,
        recovery_days=recovery_days,
        beta_mult=beta_mult,
        w_homophily=homophily,
        alpha=alpha,
        mixed=True,
    )

    # Below r0s = (r0_ord, r0_mis, r0_weighted)
    # All are identical in this simulation
    r0_records.append({"beta": beta, "r0": r0s[0]})
    tot_prop_infected_records.append({"beta": beta, "total_infected": max(R_o)})

    for day, prop in enumerate(I_o):
        daily_infection_records.append(
            {"beta": beta, "day": day, "prop_infected": prop}
        )

# Convert to dfs
r0_df = pd.DataFrame.from_records(r0_records)
daily_infection_df = pd.DataFrame.from_records(daily_infection_records)
tot_df = pd.DataFrame.from_records(tot_prop_infected_records)

### Save results ###
out_dir = os.path.join(OUT_DIR, SUB_DIR)
os.makedirs(out_dir, exist_ok=True)
r0_df.to_csv(os.path.join(out_dir, "r0s.csv"), index=False)
daily_infection_df.to_csv(os.path.join(out_dir, "daily_infections.csv"), index=False)
tot_df.to_csv(os.path.join(out_dir, "cum_infections.csv"), index=False)
