"""
Purpose: Calculate numbers presented within the abm analysis of the paper.

Input:
    - None
    - Data will be loaded from the ../../data/simulations_clean folder

Output:
    - None
    - Numbers will be printed to stdout. To create a document, you can run the
        script in the following way:
        python 016_paper_stats.py > stats_output.txt

Author: Matthew DeVerna
"""
import os

import pandas as pd

import matplotlib.pyplot as plt

# Ensure the current working directory is where this script is saved
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load data
data_dir = "../data/simulations_clean/"
fpath = os.path.join(data_dir, "2024-01-14__clean_daily_and_cum.parquet")
df = pd.read_parquet(fpath)

# Additional infections due to misinformed at peak
######################################################
largest_sample_mask = df.pop_sampled == 0.1
edges_25_mask = df.num_edges == 25

many_misinformed = df[largest_sample_mask & edges_25_mask & (df.lt_threshold == 1)]
little_misinformed = df[largest_sample_mask & edges_25_mask & (df.lt_threshold == 20)]

prop_additional_infections = (
    many_misinformed["prop_mean_infected"].max()
    - little_misinformed["prop_mean_infected"].max()
)

print(f"Additional infections due to misinformed: {prop_additional_infections:.2%}")

print("\n\n")

# Number of days between peaks
######################################################
peak_day_many = many_misinformed[
    many_misinformed["prop_mean_infected"]
    == many_misinformed["prop_mean_infected"].max()
].infection_time.item()

peak_day_little = little_misinformed[
    little_misinformed["prop_mean_infected"]
    == little_misinformed["prop_mean_infected"].max()
].infection_time.item()

number_of_days = peak_day_little - peak_day_many

print(f"Number of days between peaks: {number_of_days} days")

print("\n\n")

# Cumulative stats
######################################################
additional_infection_prop = (
    many_misinformed.prop_cum_infected.max()
    - little_misinformed.prop_cum_infected.max()
)

relative_increase = (
    additional_infection_prop / little_misinformed.prop_cum_infected.max()
)

print("Relative to largest linear threshold... ")
print(f"\t... additional % of the pop. infected: {additional_infection_prop:.2%}")
print(f"\t... % increase in pop. infected: {relative_increase:.2%}")
