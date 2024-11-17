"""
Purpose: A script to ingest and clean all experimental results. 

Inputs:
    None
    Files are loaded from: ../data/simulations

Outputs:
    Daily and cumulative results, with all parameters.


Author: Matthew DeVerna
"""
import datetime
import glob
import os

import pandas as pd
import pickle as pkl
import numpy as np

from collections import Counter

from utils import parse_cl_args, parse_config_file


def extract_parameters(file):
    """
    Return a dictionary of parameters that were used to create a contact
    network, based on the file name.
    """
    parameters = {}
    # Define the parameter names
    parameters_set = {"lt_threshold", "pop_sampled", "min_user_thresh", "num_edges"}

    # Split the file name into sections
    file_sections = file.split("__")

    # Iterate through each section to find and extract parameters
    for section in file_sections[1:]:
        for param in parameters_set:
            if param in section:
                _, value = section.split(param + "_")

                # Handles the end of the file name
                if "." in value and param != "pop_sampled":
                    # Extract the value before the file extension
                    value = value.rsplit(".", 1)[0]

                parameters[param] = value
    return parameters


def get_infected_for_all_exp(df):
    """
    Calculate the number of infected nodes at each time step for each experiment
    """

    temp_results_list = []

    for exp in df.exp.unique():
        # Select an individual experiment's results
        exp_mask = df.exp == exp
        one_exp = df[exp_mask]

        # Create dictionary where key is infection time and value is num infected
        infected_counts = Counter(one_exp.infection_time)

        # Add the experiment number, time, and number of infected to the list
        for idx in range(1, 101):
            temp_results_list.append((exp, idx, infected_counts[idx]))

    num_infected = pd.DataFrame(
        temp_results_list, columns=["experiment", "infection_time", "num_infected"]
    )
    return num_infected


if __name__ == "__main__":
    args = parse_cl_args()
    config = parse_config_file(args.config_file)

    # Used below
    frames = []
    total_nodes_map = dict()

    simulation_folder = config["PATHS"]["SIMULATION_RESULTS"]
    for file in glob.glob(os.path.join(simulation_folder, "*.parquet")):
        print(f"Cleaning {file}...")

        parameters = extract_parameters(file)
        full_path = os.path.join(simulation_folder, file)

        df = pd.read_parquet(full_path)

        # Get the total number of nodes for later
        total_nodes = df.id.nunique()
        total_nodes_map[float(parameters["pop_sampled"])] = total_nodes

        # Count the number of nodes that got infected at each time step for each experiment
        exp_infection_counts = get_infected_for_all_exp(df)

        # Calculate aggregate results (mean, std)
        agg_results = (
            exp_infection_counts.groupby(["infection_time"])["num_infected"]
            .mean()
            .reset_index()
        )
        agg_results = agg_results.rename(columns={"num_infected": "mean_infected"})
        agg_results["std"] = (
            exp_infection_counts.groupby(["infection_time"])["num_infected"]
            .std()
            .reset_index()["num_infected"]
        )

        agg_results["cum_infected"] = np.cumsum(agg_results["mean_infected"])

        # Now we calculate these relative to the total number of nodes in the network
        proportions = (
            agg_results[["mean_infected", "std", "cum_infected"]] / total_nodes
        )
        proportions = proportions.rename(
            columns={
                "mean_infected": "prop_mean_infected",
                "std": "prop_std",
                "cum_infected": "prop_cum_infected",
            }
        )

        # Combine raw counts with proportions
        agg_results = pd.concat([agg_results, proportions], axis=1)

        # Add parameters
        agg_results["pop_sampled"] = float(parameters["pop_sampled"])
        agg_results["lt_threshold"] = int(parameters["lt_threshold"])
        agg_results["num_edges"] = int(parameters["num_edges"])

        frames.append(agg_results)

    # Combine them all into a single frame
    all_experiments = pd.concat(frames)

    # Save files
    today_dtobj = datetime.datetime.today()
    today_str = datetime.datetime.strftime(today_dtobj, "%Y-%m-%d")
    out_dir = config["PATHS"]["SIMULATION_RESULTS_CLEAN"]
    outfname = os.path.join(out_dir, f"{today_str}__clean_daily_and_cum.parquet")
    all_experiments.to_parquet(outfname)

    map_out_name = os.path.join(
        out_dir, f"{today_str}__total_nodes_per_sample_size.pkl"
    )
    with open(map_out_name, "wb") as f:
        pkl.dump(total_nodes_map, f, protocol=pkl.HIGHEST_PROTOCOL)

    print("\n----- Script complete -----")
