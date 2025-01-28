"""
Purpose:
    Simulate the effects of varying homophily, the degree to which subpopulations
    only interact with their own subpopulations, SPECIFICALLY ON THE MISINFORMED GROUP.
    If homophily is .5, they interact equally with themselves and the other
    subpopulation, if it is 1, they do not interact with the other subpopulation at all.

Inputs:
    None

Outputs:
    Output Directory: sim_results/effects_of_homophily_on_misinformed
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
SUB_DIR = "effects_of_homophily_on_misinformed"
CURR_DIR = "sim_scripts"
# Ensure we are in the data_analysis directory for paths to work
os.chdir(os.path.dirname(os.path.abspath(__file__)))
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
beta = 0.15
lambduh = 3  # beta_misinformed = lambda * beta_ord

# Homophily
alphas = np.arange(0.5, 1.01, 0.05)

# Result storage
totals = []  # Total infections
infection_flows = []  # Daily infections

betas = np.arange(0.1, 0.41, 0.01)

# Run simulations
for beta in betas:
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

        I = I_o + I_m
        infection_flows.append(
            {"alpha": alpha, "beta": beta, "day": day, "prop_infected": i}
            for day, i in enumerate(I, start=1)
        )

        totals.append(
            {
                "alpha": alpha,
                "beta": beta,
                "total_ord_inf": total_ord_inf,
                "total_mis_inf": total_mis_inf,
                "total": total_ord_inf + total_mis_inf,
            }
        )

### Total proportion of the network that gets infected ###
total_infected_df = pd.DataFrame(totals)

### Daily proportion of the network that gets infected ###
daily_infected_df = pd.DataFrame(infection_flows)

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
