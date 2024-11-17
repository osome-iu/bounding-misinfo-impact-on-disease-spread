"""
Purpose: Create the list of county FIP codes that were utilized in the largest network.

Input:
    - None
    - Data will be loaded from the ../../data/simulations folder

Output:
    - None
    - Numbers will be printed to stdout. To create a document, you can run the
        script in the following way:
        python 016_paper_stats.py > stats_output.txt

Author: Matthew DeVerna
"""
import os

import pandas as pd

# Ensure the current working directory is where this script is saved
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Paths
DATA_DIR = "../data/simulations/"
OUT_DIR = "../data/intermediate_files/"

# Load data
fpath = os.path.join(
    DATA_DIR,
    # Doesn't matter which one we use here as long as it is pop_sampled_0.1
    "2023-10-18_09-52__SIR_results__lt_threshold_4__pop_sampled_0.1__min_user_thresh_200__num_edges_20__.parquet",
)
print("Loading file, this may take a while and requires ~8GBs of RAM or more...")
df = pd.read_parquet(fpath)

# Get list of unique FIPS
fips_list = df["fip"].unique()
print("Total number of unique FIPS: ", len(fips_list))

# Save to a file with one FIP per line
output_path = os.path.join(OUT_DIR, "list_of_counties.txt")
with open(output_path, "w") as f:
    for fip in fips_list:
        f.write(f"{fip}\n")

print("Script complete.")
