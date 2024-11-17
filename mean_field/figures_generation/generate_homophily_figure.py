"""
Purpose:
    Generate the figure that shows the effect of homophily.

Inputs:
    None

Outputs:
    - figures_generation/mf_homophiliy_effect.pdf

Author:
    Matthew R. DeVerna
"""
import os
import sys

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MIXED = True
OUT_DIR = "../figures"
CURR_DIR = "figures_generation"
RESULTS_DIR = "../sim_results/effects_of_homophily"
# Ensure we are in the data_analysis directory for paths to work
if os.path.basename(os.getcwd()) != CURR_DIR:
    raise Exception(f"Must run this script from the `{CURR_DIR}` directory!")

# Load simulation source code
source_dir = "../src"
sys.path.insert(0, source_dir)
from simulations import get_peak_day

### Load simulation results ###
mixed_str = "_mixed" if MIXED else ""
total_infected_df = pd.read_csv(
    os.path.join(RESULTS_DIR, f"total_infected{mixed_str}.csv")
)
daily_infected_df = pd.read_csv(
    os.path.join(RESULTS_DIR, f"daily_infected{mixed_str}.csv")
)

# Set the font size for all text
plt.rcParams.update({"font.size": 12})

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))

col_2_group = {
    "total_mis_inf": "misinformed",
    "total_ord_inf": "ordinary",
    "total": "combined",
}

group_color_map = {
    "misinformed": "#FF0060",  # red
    "ordinary": "#0079FF",  # blue
    "combined": "#9376E0",  # purple
}

homophily_color_map = {
    0.5: "#abc9c8",
    0.6: "#72aeb6",
    0.7: "#4692b0",
    0.8: "#2f70a1",
    0.9: "#134b73",
    1.0: "#0a3351",
}

### Total infected figure

for col in ["total_ord_inf", "total_mis_inf", "total"]:
    ax[0].plot(
        total_infected_df["alpha"],
        total_infected_df[col],
        color=group_color_map[col_2_group[col]],
        label="all" if col_2_group[col] == "combined" else col_2_group[col],
    )
    ax[0].scatter(
        total_infected_df["alpha"],
        total_infected_df[col],
        color=group_color_map[col_2_group[col]],
        marker="o",
        s=20,
        zorder=3,
    )

ax[0].grid(True)
ax[0].set_ylim((0, 1))
ax[0].set_yticks(np.arange(0, 1.1, 0.1))

ax[0].spines["top"].set_visible(False)
ax[0].spines["right"].set_visible(False)


ax[0].set_ylabel("proportion of population infected")
ax[0].set_xlabel(r"$\alpha$")


# Specify the desired order of legend labels
desired_order = ["all", "misinformed", "ordinary"]

# Get the handles and labels of the current legend
handles, labels = ax[0].get_legend_handles_labels()

# Create a dictionary to map labels to handles
handle_dict = dict(zip(labels, handles))

# Create a list of handles in the desired order
sorted_handles = [handle_dict[label] for label in desired_order]

# Create a list of labels in the desired order
sorted_labels = desired_order

# Create the legend with the desired order
ax[0].legend(sorted_handles, sorted_labels)


### Daily infections figure

values_to_match = [0.6, 0.7, 0.8, 0.9, 1.0]

daily_infected_df.alpha = daily_infected_df.alpha.astype(float)
less_daily = daily_infected_df[
    np.isin(daily_infected_df.alpha.round(2), values_to_match)
]


for alpha in less_daily.alpha.round(2).unique():
    temp_df = less_daily[
        np.isclose(less_daily.alpha, alpha)  # Pandas float storage is so annoying
    ]

    ax[1].plot(
        temp_df["day"],
        temp_df["prop_infected"],
        color=homophily_color_map[alpha],
        label=alpha,
    )

# Add arrow
highest_point = less_daily[np.isclose(less_daily.alpha, 0.6)]
h_max_prop = highest_point["prop_infected"].max()
h_max_day = get_peak_day(highest_point["prop_infected"])

lowest_point = less_daily[np.isclose(less_daily.alpha, 1.0)]
l_max_prop = lowest_point["prop_infected"].max()
l_max_day = get_peak_day(lowest_point["prop_infected"])

arr_buffer = 0.005
text_buffer = 0.005

# Create a curved arrow patch
arrow = patches.FancyArrowPatch(
    (h_max_day + 1, h_max_prop + arr_buffer),  # Starting point (x, y)
    (l_max_day - 1, l_max_prop + arr_buffer),  # Ending point (x, y)
    connectionstyle="arc3,rad=.18",  # Connection style for the arrow
    arrowstyle="->",  # Arrow style
    linewidth=1,  # Arrow linewidth
    edgecolor="black",  # Arrow edge color
    mutation_scale=10,
    zorder=3,
)
ax[1].add_patch(arrow)

# Add an annotation above the arrow
middle_x = 13
middle_y = 0.275
ax[1].annotate(
    "More\nhomophily",
    xy=(middle_x, middle_y),  # Annotation position (x, y)
    xytext=(middle_x, middle_y),  # Text position (x, y)
    ha="center",  # Horizontal alignment
    va="bottom",  # Vertical alignment
    fontsize=10,
    zorder=3,
)

ax[1].set_ylim(0, 0.4)
ax[1].set_xlim(0, 100)
ax[0].set_ylim(0.25, 1.01)
ax[0].set_xlim(0.49, 1.01)

ax[1].grid(True)
# Move the y-axis of the right spanning plot to the right side
ax[1].yaxis.tick_right()
ax[1].yaxis.set_label_position("right")

ax[1].spines["top"].set_visible(False)
ax[1].spines["left"].set_visible(False)

ax[1].legend(title=r"$\alpha$")

ax[1].set_ylabel("proportion of population infected", rotation=-90, va="bottom")
ax[1].set_xlabel("day")

plt.tight_layout()

plt.subplots_adjust(wspace=0.1)

# Add subplot annotations
ax[0].annotate(
    "A",
    xy=(-0.11, 1),
    xycoords=ax[0].transAxes,
    fontsize=14,
    fontweight="bold",
    ha="center",
    va="center",
)
ax[1].annotate(
    "B",
    xy=(-0.05, 1),
    xycoords=ax[1].transAxes,
    fontsize=14,
    fontweight="bold",
    ha="center",
    va="center",
)

# Save the plot
os.makedirs(OUT_DIR, exist_ok=True)
plt.savefig(os.path.join(OUT_DIR, f"mf_homophily_effect{mixed_str}.pdf"), dpi=800)
plt.savefig(
    os.path.join(OUT_DIR, f"mf_homophily_effect{mixed_str}.png"),
    dpi=800,
    transparent=True,
)
