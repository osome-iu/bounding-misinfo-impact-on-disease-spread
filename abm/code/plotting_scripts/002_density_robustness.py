"""
Purpose: Generate a figure that illustrates the robustness of our results as a
    function of the network density.

Input:
    - None
    - Data will be loaded from the ../../data/simulations_clean folder

Output:
    The figure (pdf)

Author: Matthew DeVerna
"""
import os

import pandas as pd
import matplotlib.pyplot as plt

from collections import defaultdict
from matplotlib.ticker import FuncFormatter

plt.rcParams.update({"font.size": 14})

# Ensure the current working directory is where this script is saved
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Set paths/files
output_dir = "../../data/figures/"
data_dir = "../../data/simulations_clean"
fpath = os.path.join(data_dir, "2024-01-14__clean_daily_and_cum.parquet")

df = pd.read_parquet(fpath)

# For the largest network, we want to calculate the relative and percentage increase
df = df[df.pop_sampled == 0.1].copy().reset_index(drop=True)

# There is an easier way to do this with groupby, but we use the dictionary later
max_cum_infected = defaultdict(dict)
for selected_pair, temp_data in df.groupby(["num_edges", "lt_threshold"]):
    num_edges, lt_thresh = selected_pair

    max_cum_infected[num_edges].update(
        {lt_thresh: temp_data["prop_cum_infected"].max()}
    )
max_cum_infected = dict(max_cum_infected)

# Convert to a dataframe
cum_infected_df = (
    pd.DataFrame.from_dict(max_cum_infected).reset_index().melt(id_vars="index")
)
cum_infected_df = cum_infected_df.rename(
    columns={"index": "lt_threshold", "variable": "num_edges", "value": "cum_infected"}
)

# Calculate relative increases/percent changes dictionaries
relative_increases = defaultdict(dict)
percent_change = defaultdict(dict)

for pop_sampled, max_vals in max_cum_infected.items():
    twenty_cum = max_vals[20]  # Always use 20 because k = 25 is in main text

    for lt, max_val in max_vals.items():
        change = max_val - twenty_cum
        relative_increases[pop_sampled].update({lt: change / twenty_cum})
        percent_change[pop_sampled].update({lt: change})
relative_increases = dict(relative_increases)
percent_change = dict(percent_change)

relative_increase_df = (
    pd.DataFrame.from_dict(relative_increases)
    .reset_index()
    .rename(columns={"index": "lt_thresh"})
)

# Create the data frame
relative_increase_df = relative_increase_df.melt(
    id_vars="lt_thresh", var_name="num_edges", value_name="relative_increase"
)

relative_increase_df["num_edges"] = relative_increase_df["num_edges"].astype(int)
relative_increase_df["lt_thresh"] = relative_increase_df["lt_thresh"].astype(int)

relative_increase_df = relative_increase_df.sort_values(by=["num_edges", "lt_thresh"])

percent_change_df = (
    pd.DataFrame.from_dict(percent_change)
    .reset_index()
    .rename(columns={"index": "lt_thresh"})
)

# Create the data frame
percent_change_df = percent_change_df.melt(
    id_vars="lt_thresh", var_name="num_edges", value_name="percent_change"
)

percent_change_df["num_edges"] = percent_change_df["num_edges"].astype(int)
percent_change_df["lt_thresh"] = percent_change_df["lt_thresh"].astype(int)

percent_change_df = percent_change_df.sort_values(by=["num_edges", "lt_thresh"])


# Create the figure
#
def percentage_formatter_w_dec(x, pos):
    return f"{100 * x:.2f}%"


def percentage_formatter(x, pos):
    return f"{100 * x:.0f}%"


def no_decimals(x, pos):
    return f"{x:.0f}"


fig, (ax1, ax2) = plt.subplots(ncols=2, nrows=1, figsize=(10, 5))

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

# Plot total infected.
cum_infected_df["num_edges"] = cum_infected_df["num_edges"].astype(int)
cum_infected_df.sort_values(by=["lt_threshold", "num_edges"], inplace=True)
lt1 = cum_infected_df[cum_infected_df.lt_threshold == 1]

lt1_rel = relative_increase_df[relative_increase_df.lt_thresh == 1]

ax1.plot(lt1["num_edges"], lt1["cum_infected"], color="blue", marker="o")

ax1.set_ylim(0, 0.6)

ax1.set_ylabel("Total percentage\nof population infected", color="blue")
ax1.set_xlabel(r"$\bar{k}$")

# Create a second Y axis on the right
ax1_ = ax1.twinx()

# Plot the second data on the right Y axis (log scale)
ax1_.semilogy(
    lt1_rel["num_edges"], lt1_rel["relative_increase"], color="red", marker="o"
)
ax1_.set_ylabel(
    "Relative increase\nof population infected\n" + r"(versus $\phi = 20$)",
    color="red",
    rotation=-90,
    labelpad=50,
)

ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)


ax2.yaxis.set_label_position("right")
ax2.yaxis.tick_right()

for lt, temp_data in percent_change_df.groupby("lt_thresh"):
    if lt == 20:
        continue
    num_edges = temp_data["num_edges"].values
    relative_vals = temp_data["percent_change"].values

    ax2.plot(
        num_edges,
        relative_vals,
        label=f"{lt}",
        marker=marker_map[lt],
        linestyle=line_map[lt],
        linewidth=2,
        zorder=3,
    )

ax2.set_xlabel(r"$\bar{k}$")
ax2.set_ylabel(
    "Additional percentage\nof population infected\n" + r"(versus $\phi = 20$)",
    rotation=-90,
    labelpad=50,
)

# ax2.spines['top'].set_visible(False)
# ax2.spines['left'].set_visible(False)

ax2.xaxis.set_major_formatter(FuncFormatter(no_decimals))
ax2.yaxis.set_major_formatter(FuncFormatter(percentage_formatter))
ax1.yaxis.set_major_formatter(FuncFormatter(percentage_formatter))

ax2.legend(
    loc="upper center",
    ncol=3,
    columnspacing=0.8,
    title=r"$\phi$",
    fontsize=12,
    #     title_fontsize='large',
    bbox_to_anchor=(0.5, 1.3),
    bbox_transform=ax2.transAxes,
    frameon=True,
)

ax1.grid(zorder=0)
ax2.grid(zorder=0)

plt.subplots_adjust(wspace=0.6)

# Add subplot annotations
ax1.annotate(
    "(a)",
    xy=(-0.25, 1.05),
    xycoords=ax1.transAxes,
    fontsize=14,
    ha="center",
    va="center",
)
ax2.annotate(
    "(b)",
    xy=(-0.1, 1.05),
    xycoords=ax2.transAxes,
    fontsize=14,
    ha="center",
    va="center",
)

# Save the figure
outpath = os.path.join(output_dir, "average_degree.pdf")
fig.savefig(outpath, dpi=800, bbox_inches="tight")

print("Script complete.")
