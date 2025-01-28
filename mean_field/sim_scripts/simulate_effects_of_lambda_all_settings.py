"""
Purpose:
    Simulate the effects of varying lambda (lambda = beta_m / beta_o), given many different
    parameter settings.

Inputs:
    None

Outputs:
    Output Directory: sim_results/effects_of_lambda
    - total_infected_all_settings.csv : the total proportion of the network that gets infected
    - daily_infected_all_settings.csv : proportion of the network infected by day

Author:
    Matthew R. DeVerna
"""

import os
import sys

import numpy as np
import pandas as pd

OUT_DIR = "../sim_results"
SUB_DIR = "effects_of_lambda"
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

# Initial proportion of ordinary people
x = 1 - np.array([0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5])
x = x[::-1]
prop_infected = 0.001  # Initial proportion of infected

# beta_misinformed = lambda * beta_ord
lambdas_low = np.arange(1, 10.2, 0.2)
lambdas_mid = np.arange(10, 110, 10)
lambdas_high = np.arange(110, 1100, 100)
lambdas = np.concatenate([lambdas_low, [3.33], lambdas_mid, lambdas_high])
lambdas = sorted([round(val, 2) for val in lambdas])

# Fixed based on results from previous analyses
betas = [0.001, 0.01, 0.1, 0.2, 0.3]
rec_days = 5

# Result storage
totals = []  # Total infections
# Will store the progression of infections over time, indexed by parameter settings
infection_flows_ord = dict()
infection_flows_mis = dict()

for beta in betas:
    for lambduh in lambdas:
        for frac_ord in x:
            # Run the simulation based on the input
            S_o, S_m, I_o, I_m, R_o, R_m, r0s = run_simulation(
                frac_ord=frac_ord,
                prop_infec=prop_infected,
                num_days=num_days,
                beta_ord=beta,
                recovery_days=rec_days,
                beta_mult=lambduh,
                w_homophily=False,
                alpha=None,
                mixed=True,
            )

            # Daily incidence
            infection_flows_ord[(np.round(lambduh, 1), beta, frac_ord)] = I_o
            infection_flows_mis[(np.round(lambduh, 1), beta, frac_ord)] = I_m

            # Total infected
            total_ord_inf = max(R_o)
            total_mis_inf = max(R_m)
            totals.append(
                {
                    "total_ord_inf": total_ord_inf,
                    "total_mis_inf": total_mis_inf,
                    "lambda": lambduh,
                    "beta": beta,
                    "frac_ord": frac_ord,
                    "diff": total_mis_inf - total_ord_inf,
                    "total_inf": total_ord_inf + total_mis_inf,
                    "r0": r0s[-1],
                }
            )

# Convert total infections to a DataFrame
totals_df = pd.DataFrame.from_records(totals)

# Calculate total "extra" infections compared to lambda = 1
all_frames = []
for group, frame in totals_df.groupby(["beta", "frac_ord"]):
    frame["extra_inf"] = (
        frame["total_inf"] - frame[frame["lambda"] == 1]["total_inf"].values[0]
    )
    all_frames.append(frame)
totals_df = pd.concat(all_frames)

# Include the fraction of misinformed
totals_df["frac_mis"] = round(1 - totals_df["frac_ord"], 3)

# Convert daily infection results into a dataframe
mis_data = [
    (day, lambda_, beta, frac_ord, infection)
    for (lambda_, beta, frac_ord), infections in infection_flows_mis.items()
    for day, infection in enumerate(infections, start=1)
]
ord_data = [
    (day, lambda_, beta, frac_ord, infection)
    for (lambda_, beta, frac_ord), infections in infection_flows_ord.items()
    for day, infection in enumerate(infections, start=1)
]

mis_df = pd.DataFrame(
    mis_data, columns=["day", "lambda", "beta", "frac_ord", "infections"]
)
ord_df = pd.DataFrame(
    ord_data, columns=["day", "lambda", "beta", "frac_ord", "infections"]
)

by_day_results = mis_df.merge(
    ord_df, on=["day", "lambda", "beta", "frac_ord"], suffixes=("_mis", "_ord")
)

by_day_results["infections_total"] = (
    by_day_results["infections_mis"] + by_day_results["infections_ord"]
)

### Save results ###
out_dir = os.path.join(OUT_DIR, SUB_DIR)
os.makedirs(out_dir, exist_ok=True)
totals_df.to_csv(os.path.join(out_dir, "total_infected_all_settings.csv"), index=False)
by_day_results.to_csv(
    os.path.join(out_dir, "daily_infected_all_settings.csv"), index=False
)
