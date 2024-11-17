"""
Purpose:
    Simulate the effects of varying homophily, the degree to which subpopulations
    only interact with their own subpopulations. If homophily is .5, they interact
    equally with themselves and the other subpopulation, if it is 1, they do not
    interact with the other subpopulation at all.

Inputs:
    None

Outputs:
    Output Directory: sim_results/effects_of_homophily
    - total_infected.csv : the total proportion of the network that gets infected
    - daily_infected.csv : proportion of the network infected by day

Author:
    Matthew R. DeVerna
"""
import os
import sys

import numpy as np
import pandas as pd

MIXED = True
OUT_DIR = "../sim_results"
SUB_DIR = "effects_of_homophily"
CURR_DIR = "sim_scripts"
# Ensure we are in the data_analysis directory for paths to work
if os.path.basename(os.getcwd()) != CURR_DIR:
    raise Exception(f"Must run this script from the `{CURR_DIR}` directory!")

# Load simulation source code
source_dir = "../src"
sys.path.insert(0, source_dir)
from simulations import run_simulation

### SET SIMULATION PARAMETERS ###
num_days = 100
x = 0.5  # Initial proportion of ordinary people
prop_infected = 0.001  # Initial proportion of infected
rec_days = 5

# Fixed based on results from previous analyses
beta = 0.3
lambduh = 3  # beta_misinformed = lambda * beta_ord

# Homophily
alphas = np.arange(0.5, 1.02, 0.02)

# Result storage
totals = []  # Total infections
infection_flows = dict()  # Daily infections

# Run simulations
for alpha in alphas:
    # Run the simulation based on the input
    S_o, S_m, I_o, I_m, R_o, R_m, r0s = run_simulation(
        frac_ord=x,
        prop_infec=prop_infected,
        num_days=num_days,
        beta_ord=beta,
        recovery_days=rec_days,
        beta_mult=lambduh,
        w_homophily=True,
        alpha=alpha,
        mixed=MIXED,
    )
    total_ord_inf = max(R_o)
    total_mis_inf = max(R_m)

    infection_flows[alpha] = I_o + I_m

    totals.append(
        {
            "alpha": alpha,
            "total_ord_inf": total_ord_inf,
            "total_mis_inf": total_mis_inf,
            "total": total_ord_inf + total_mis_inf,
        }
    )

### Total proportion of the network that gets infected ###
total_infected_df = pd.DataFrame(totals)

### Daily proportion of the network that gets infected ###
daily_infected_df = pd.DataFrame(infection_flows).reset_index()
daily_infected_df = daily_infected_df.rename(columns={"index": "day"})
daily_infected_df.day = daily_infected_df.day + 1
daily_infected_df = daily_infected_df.melt(id_vars="day")
daily_infected_df.rename(columns={"variable": "alpha"}, inplace=True)
daily_infected_df.rename(columns={"value": "prop_infected"}, inplace=True)

### Save results ###
out_dir = os.path.join(OUT_DIR, SUB_DIR)
os.makedirs(out_dir, exist_ok=True)
mixed_str = "_mixed" if MIXED else ""
total_infected_df.to_csv(
    os.path.join(out_dir, f"total_infected{mixed_str}.csv"), index=False
)
daily_infected_df.to_csv(
    os.path.join(out_dir, f"daily_infected{mixed_str}.csv"), index=False
)
