"""
Purpose:
    Simulate the effects of varying lambda (lambda = beta_m / beta_o).

Inputs:
    None

Outputs:
    Output Directory: sim_results/effects_of_lambda
    - total_infected.csv : the total proportion of the network that gets infected
    - daily_infected.csv : proportion of the network infected by day

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
x = 0.5  # Initial proportion of ordinary people
prop_infected = 0.001  # Initial proportion of infected
lambdas = np.arange(1, 3.2, 0.2)  # beta_misinformed = lambda * beta_ord
lambdas = np.append(lambdas, 3.33)

# Fixed based on results from previous analyses
beta = 0.3
rec_days = 5

# Result storage
totals = []  # Total infections

# Will store the progression of infections over time, indexed by lambda
infection_flows_ord = dict()
infection_flows_mis = dict()

for lambduh in lambdas:
    # Run the simulation based on the input
    S_o, S_m, I_o, I_m, R_o, R_m, r0s = run_simulation(
        frac_ord=x,
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
    infection_flows_ord[np.round(lambduh, 1)] = I_o
    infection_flows_mis[np.round(lambduh, 1)] = I_m

    # Total infected
    total_ord_inf = max(R_o)
    total_mis_inf = max(R_m)
    totals.append(
        {
            "total_ord_inf": total_ord_inf,
            "total_mis_inf": total_mis_inf,
            "lambda": lambduh,
            "diff": total_mis_inf - total_ord_inf,
            "total_inf": total_ord_inf + total_mis_inf,
        }
    )

### Total proportion of the network that gets infected ###
totals_df = pd.DataFrame.from_records(totals)
totals_df["total_extra"] = totals_df["total_inf"] - totals_df["total_inf"].min()

### Daily proportion of the network that gets infected ###
# ----- Combined subpopulations -----
combined_infections = pd.DataFrame(infection_flows_ord) + pd.DataFrame(
    infection_flows_mis
)
combined_infections = combined_infections.reset_index()
combined_infections = combined_infections.rename(columns={"index": "day"})
combined_infections.day = combined_infections.day + 1  # Days start on 1
combined_infections = combined_infections.melt(id_vars="day")
combined_infections.rename(columns={"variable": "lambda"}, inplace=True)
combined_infections["group"] = "combined"

# ----- Ordinary subpopulation -----
infections_ord = pd.DataFrame(infection_flows_ord).reset_index()
infections_ord = infections_ord.rename(columns={"index": "day"})
infections_ord.day = infections_ord.day + 1
infections_ord = infections_ord.melt(id_vars="day")
infections_ord.rename(columns={"variable": "lambda"}, inplace=True)
infections_ord["group"] = "ordinary"

# ----- Misinformed subpopulation -----
infections_mis = pd.DataFrame(infection_flows_mis).reset_index()
infections_mis = infections_mis.rename(columns={"index": "day"})
infections_mis.day = infections_mis.day + 1
infections_mis = infections_mis.melt(id_vars="day")
infections_mis.rename(columns={"variable": "lambda"}, inplace=True)
infections_mis["group"] = "misinformed"

# Combine them into one dataframe
by_day_results = pd.concat((infections_mis, infections_ord, combined_infections))

### Save results ###
out_dir = os.path.join(OUT_DIR, SUB_DIR)
os.makedirs(out_dir, exist_ok=True)
totals_df.to_csv(os.path.join(out_dir, "total_infected.csv"), index=False)
by_day_results.to_csv(os.path.join(out_dir, "daily_infected.csv"), index=False)
