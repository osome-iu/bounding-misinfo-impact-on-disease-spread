"""
Purpose: Generate a figure that illustrates the effect of the size of the misinformed
    population on the number of infections.

Input:
    - None
    - Data will be loaded from the ../../data/simulations_clean folder

Output:
    The figure (pdf)

Author: Matthew DeVerna
"""
import os

import pickle as pkl
import pandas as pd

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams.update({"font.size": 14})


# Ensure the current working directory is where this script is saved
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# Set up the relative paths/files
data_dir = "../../data/simulations_clean/"
intermediate_dir = "../../data/intermediate_files/"
output_dir = "../../data/figures/"
net_size_fp = "../../data/simulations_clean/2024-01-14__total_nodes_per_sample_size.pkl"

# Load the daily and cumulative trends data
trends_file = os.path.join(data_dir, "2024-01-14__clean_daily_and_cum.parquet")
trends_df = pd.read_parquet(trends_file)

# Select the trends for only the largest network tested
big_net_trends = (
    trends_df[trends_df["pop_sampled"] == 0.1].reset_index(drop=True).copy()
)

# Load the pickle file that contains the node IDs of the misinformed nodes
misinfo_nodes_per_lt_file = os.path.join(intermediate_dir, "LT_output.pkl")
with open(misinfo_nodes_per_lt_file, "rb") as f:
    misinfo_nodes_per_lt_data = pkl.load(f)

# Convert to a dataframe
results = []
for lt_threshold, num_misinformed in misinfo_nodes_per_lt_data.items():
    results.append(
        {"lt_threshold": lt_threshold, "num_misinformed": len(num_misinformed)}
    )
misinfo_nodes_per_lt_df = pd.DataFrame.from_records(results)

# Load the number of nodes per sample size
with open(net_size_fp, "rb") as f:
    num_nodes = pkl.load(f)


# Set up stuff for the plotting later
thresholds = [int(val) for val in trends_df.lt_threshold.unique() if val not in [4, 10]]

thresholds.sort()

colors = [
    "#efc565",
    "#56b4e9",
    "#009e73",
    "#f0e442",
    "#000000",
    "#0072b2",
    "#d55e00",
    "#cc79a7",
]
markers = ["<", ">", "^", "o", "s", "d"]

# Create color map based on Tableu10 found here: https://vega.github.io/vega/docs/schemes/
color_map = {1: "#4c78a8", 2: "#f58518", 5: "#e45756", 20: "#72b7b2"}


### Start figure creation ###
# -----------------------------------------------------------
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(13, 5))


# Create the first figure: misinformed nodes X linear threshold
# ------------------------------------------------------------
ax[0].plot(
    misinfo_nodes_per_lt_df["lt_threshold"],
    misinfo_nodes_per_lt_df["num_misinformed"] / num_nodes[0.1],
    color="black",
    linewidth=2,
    zorder=3,
)
ax[0].scatter(
    misinfo_nodes_per_lt_df["lt_threshold"],
    misinfo_nodes_per_lt_df["num_misinformed"] / num_nodes[0.1],
    color="black",
    zorder=3,
)

for idx, thresh in enumerate(thresholds):
    num_mis = (
        misinfo_nodes_per_lt_df[
            misinfo_nodes_per_lt_df["lt_threshold"] == thresh
        ].num_misinformed.item()
        / num_nodes[0.1]
    )
    ax[0].scatter(thresh, num_mis, color=color_map[thresh], s=50, marker="s", zorder=3)

ax[0].set_xscale("log")
# ax[0].set_ylim((0,120000))

x_vals = [1, 2, 5, 10, 20, 50, 100]

ax[0].set_xticks(x_vals)
ax[0].get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())

# ax[0].get_yaxis().set_major_formatter(
#     mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

ax[0].set_xlabel(r"$\phi$")
# ax[0].set_ylabel("Number of misinformed nodes")
ax[0].set_ylabel("Proportion of network misinformed")

sns.despine(ax=ax[0])
ax[0].grid(zorder=0)


# Create the second figure: daily incidence
# ------------------------------------------------------------
biggest_y = 0
for idx, thresh in enumerate(thresholds):
    lt_mask = (big_net_trends.lt_threshold == thresh) & (big_net_trends.num_edges == 25)
    temp_frame = big_net_trends[lt_mask]

    biggest_y = max(biggest_y, temp_frame["prop_mean_infected"].max())

    ax[1].plot(
        temp_frame.loc[:, "infection_time"],
        temp_frame.loc[:, "prop_mean_infected"],
        color=color_map[thresh],
        linewidth=1,
        label=f"{thresh}",
    )

    ax[1].fill_between(
        temp_frame["infection_time"],
        temp_frame["prop_mean_infected"] - temp_frame["prop_std"],
        temp_frame["prop_mean_infected"] + temp_frame["prop_std"],
        alpha=0.5,
        color=color_map[thresh],
    )

# May need to be updated if replicated results are used
ax[1].set_ylim((0, 0.12))
ax[1].set_xlim((0, 60))

ax[1].set_xlabel("day")
ax[1].set_ylabel("Proportion of network infected")

sns.despine(ax=ax[1])
ax[1].grid()


# Create the second figure: cumulative infection proportion
# ------------------------------------------------------------

for idx, thresh in enumerate(thresholds):
    lt_mask = (big_net_trends.lt_threshold == thresh) & (big_net_trends.num_edges == 25)
    temp_frame = big_net_trends[lt_mask]

    ax[2].plot(
        temp_frame.loc[:, "infection_time"],
        temp_frame.loc[:, "prop_cum_infected"],
        color=color_map[thresh],
        linewidth=1,
        label=f"{thresh}",
    )

    ax[2].fill_between(
        temp_frame["infection_time"],
        temp_frame["prop_cum_infected"] - temp_frame["prop_std"],
        temp_frame["prop_cum_infected"] + temp_frame["prop_std"],
        alpha=0.5,
        color=color_map[thresh],
    )
ax[2].set_ylim((0, 0.6))
ax[2].set_xlim((0, 60))

# ax[2].yaxis.set_label_position('right')
# ax[2].yaxis.set_ticks_position('right')

ax[2].set_xlabel("day")
ax[2].set_ylabel(
    "Cumulative proportion\nof network infected"
)  # , rotation=270, va='bottom')

ax[2].legend(title=r"$\phi$", ncol=1)

ax[2].spines["top"].set_visible(False)
# ax[2].spines['left'].set_visible(True)
ax[2].spines["right"].set_visible(False)
ax[2].grid()


plt.tight_layout()
plt.subplots_adjust(wspace=0.45)

# Add annotations
ax[0].annotate(
    "A",
    xy=(-0.4, 0.981),
    xycoords=ax[0].transAxes,
    ha="center",
    fontsize=16,
    fontweight="bold",
)
ax[1].annotate(
    "B",
    xy=(-0.35, 0.981),
    xycoords=ax[1].transAxes,
    ha="center",
    fontsize=16,
    fontweight="bold",
)
ax[2].annotate(
    "C",
    xy=(-0.28, 0.981),
    xycoords=ax[2].transAxes,
    ha="center",
    fontsize=16,
    fontweight="bold",
)

# Save the figure
outpath = os.path.join(
    output_dir, "effect_of_increasing_misinformation_in_net_prop.pdf"
)
fig.savefig(outpath, dpi=600, bbox_inches="tight")

print("Script complete.")
