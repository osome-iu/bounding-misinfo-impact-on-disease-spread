"""
Purpose: Generate a figure that illustrates the robustness of our results as a
    function of the network sampling proportion.

Input:
    - None
    - Data will be loaded from the ../../data/simulations_clean folder

Output:
    The figure (pdf)

Author: Matthew DeVerna
"""
import os

import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt

from collections import defaultdict
from matplotlib.ticker import FuncFormatter

mpl.rcParams["font.size"] = 14

# Ensure the current working directory is where this script is saved
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Set output paths/files
output_dir = "../../data/figures/"
data_dir = "../../data/simulations_clean"

# Load the daily and cumulative trends data
fpath = os.path.join(data_dir, "2024-01-14__clean_daily_and_cum.parquet")
df = pd.read_parquet(fpath)

# Take only the number of edges that we report in the main text
df = df[df.num_edges == 25].copy().reset_index(drop=True)

# Get the maximum cumulative infection for each threshold
max_cum_infected = defaultdict(dict)
for selected_pair, temp_data in df.groupby(["pop_sampled", "lt_threshold"]):
    pop_sampled, lt_thresh = selected_pair

    max_cum_infected[pop_sampled].update(
        {lt_thresh: temp_data["prop_cum_infected"].max()}
    )
max_cum_infected = dict(max_cum_infected)

# Calculate the relative increase
relative_increases = defaultdict(dict)
for pop_sampled, max_vals in max_cum_infected.items():
    twenty_cum = max_vals[20]

    for lt, max_val in max_vals.items():
        relative_increases[pop_sampled].update(
            {lt: (max_val - twenty_cum) / twenty_cum}
        )

relative_increases = dict(relative_increases)
relative_increase_df = (
    pd.DataFrame.from_dict(relative_increases)
    .reset_index()
    .rename(columns={"index": "lt_thresh"})
)

# Reshape the frame
relative_increase_df = relative_increase_df.melt(
    id_vars="lt_thresh", var_name="pop_sampled", value_name="relative_increase"
)

relative_increase_df = relative_increase_df.sort_values(by=["pop_sampled", "lt_thresh"])


# Create the figure
def percentage_formatter_w_dec(x, pos):
    return f"{100 * x:.2f}%"


def percentage_formatter(x, pos):
    return f"{100 * x:.0f}%"


fig, ax = plt.subplots(figsize=(8, 6))

marker_map = {
    1: "<",
    2: ">",
    4: "^",
    5: "o",
    10: "d",
    20: "s",
}

line_map = {
    1: "dashed",
    2: "dotted",
    4: "dashdot",
    5: "dashed",
    10: "dotted",
    20: "dashdot",
}

color_map = {
    1: "dashed",
    2: "dotted",
    4: "dashdot",
    5: "dashed",
    10: "dotted",
    20: "dashdot",
}


for lt, temp_data in relative_increase_df.groupby("lt_thresh"):
    if lt == 20:
        continue
    pop_sampled = temp_data["pop_sampled"].values
    relative_vals = temp_data["relative_increase"].values

    ax.plot(
        pop_sampled,
        relative_vals,
        label=f"{lt:.0f}",
        #         color = color_map[lt],
        marker=marker_map[lt],
        linestyle=line_map[lt],
        linewidth=2,
    )

plt.legend(title=r"$\phi$", ncol=2)

ax.set_xlabel("Sample size")
ax.set_ylabel(
    "Relative increase in\ntotal population infected\n" + r"(versus $\phi = 20$)"
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.set_xscale("log")

ax.xaxis.set_major_formatter(FuncFormatter(percentage_formatter_w_dec))
ax.yaxis.set_major_formatter(FuncFormatter(percentage_formatter))

plt.grid()

# Save the figure
outpath = os.path.join(output_dir, "relative_increase_from_sample_size.pdf")
fig.savefig(outpath, dpi=800, bbox_inches="tight")

print("Script complete.")
