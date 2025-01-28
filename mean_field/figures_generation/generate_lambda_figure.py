"""
Purpose:
    Generate the figure that shows the effect of lambda.

Inputs:
    None

Outputs:
    - figures_generation/mf_lambda_effect.pdf

Author:
    Matthew R. DeVerna
"""

import os
import sys

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd


OUT_DIR = "../figures"
CURR_DIR = "figures_generation"
RESULTS_DIR = "../sim_results/effects_of_lambda"
# Ensure we are in the data_analysis directory for paths to work
if os.path.basename(os.getcwd()) != CURR_DIR:
    raise Exception(f"Must run this script from the `{CURR_DIR}` directory!")

# Load simulation source code
source_dir = "../src"
sys.path.insert(0, source_dir)
from simulations import get_peak_day

### Load simulation results ###
totals_df = pd.read_csv(os.path.join(RESULTS_DIR, "total_infected_all_settings.csv"))
by_day_df = pd.read_csv(os.path.join(RESULTS_DIR, "daily_infected_all_settings.csv"))

# Select specific lambda values and parameter settings
temp_df = by_day_df[
    (by_day_df["lambda"].isin([1, 2, 3]))  # , 3.3, 4]))
    & (by_day_df["beta"] == 0.3)
    & (by_day_df["frac_ord"] == 0.5)
]

# Create the figure and grid layout
fig = plt.figure(figsize=(10, 6))
grid = gridspec.GridSpec(3, 2, width_ratios=[1, 2])

# Create subplots for the first column
ax1 = plt.subplot(grid[0, 1])
ax2 = plt.subplot(grid[1, 1])
ax3 = plt.subplot(grid[2, 1])

color_list = [
    "#006ba4",
    "#ff800e",
    "#ababab",
    "#595959",
    "#5f9ed1",
    "#c85200",
    "#898989",
    "#a2c8ec",
    "#ffbc79",
    "#cfcfcf",
]
color_map = {val: color_list[idx] for idx, val in enumerate([1, 2, 3, 4])}
line_map = {1: "dotted", 2: "dashed", 3: "solid", 4: "dashdot"}

# Set the font size for all text
plt.rcParams.update({"font.size": 12})

# Used to store/plot the peaks
# y_buffer = 0.02
peaks_dict = {}

# Plot the curves
for lambda_val in temp_df["lambda"].unique():
    selected_df = temp_df[temp_df["lambda"] == lambda_val]

    peaks_dict[lambda_val] = {
        "x": get_peak_day(selected_df["infections_total"]),
        "y": selected_df["infections_total"].max(),
    }

    ax1.plot(
        selected_df["day"],
        selected_df["infections_total"],
        c=color_map[lambda_val],
        linestyle=line_map[lambda_val],
        label=f"{lambda_val}",
    )
    ax2.plot(
        selected_df["day"],
        selected_df["infections_mis"],
        c=color_map[lambda_val],
        linestyle=line_map[lambda_val],
        label=f"{lambda_val}",
    )
    ax3.plot(
        selected_df["day"],
        selected_df["infections_ord"],
        c=color_map[lambda_val],
        linestyle=line_map[lambda_val],
        label=f"{lambda_val}",
    )

# Add peaks to the totals plot
for lambda_val, peak in peaks_dict.items():
    if lambda_val in [1, 3]:
        ax1.vlines(
            x=peak["x"],
            ymin=0,
            ymax=peak["y"],
            color="black",
            linewidth=1,
        )
        ax1.text(
            peak["x"],
            peak["y"],
            f"{peak['y']:.2f} (day {peak['x']})",
            ha="left",
            va="bottom",
            color="black",
        )

# Remove all spines
for a in [ax1, ax2, ax3]:
    a.spines["top"].set_visible(False)
    a.spines["right"].set_visible(False)
    a.grid()
    a.set_ylim(0, 0.4)


# Reorder the legend handles by row instead of column
h, l = ax1.get_legend_handles_labels()
reorder = lambda l, nc: sum((l[i::nc] for i in range(nc)), [])
ax1.legend(
    # reorder(h, 3),
    # reorder(l, 3),
    ncol=4,
    loc="lower center",
    bbox_to_anchor=(0.5, 1),
    frameon=False,
    title=r"$\lambda$",
)

# Create subplot for the second column spanning all three rows
# ax5 = plt.subplot(grid[:, 1])
ax5 = plt.subplot(grid[2, 0])

# Plot extra infections
source = totals_df[
    (totals_df["beta"] == 0.3)
    & (totals_df["frac_ord"] == 0.5)
    & (totals_df["lambda"] <= 10)
]
ax5.plot(
    source["lambda"],
    source["extra_inf"],
    color="black",
    alpha=1,
    linewidth=1,
)

# plot points for lambda = [ 1, 2, 3] that match the colors of the other plots
# for lambda_val in [1, 2, 3]:
#     ax5.scatter(
#         lambda_val,
#         source[source["lambda"] == lambda_val]["extra_inf"],
#         color=color_map[lambda_val],
#         marker="s",
#         alpha=1,
#         zorder=3,
#     )

ax5.set_xlabel(r"$\lambda$")
ax5.set_ylim(0, 0.3)
ax5.spines["top"].set_visible(False)
ax5.spines["right"].set_visible(False)
ax5.grid()
# ax5.set_xscale("log")

# Move the y-axis of the right spanning plot to the right side
# ax5.yaxis.tick_right()
# ax5.yaxis.set_label_position("right")

ax1.set_ylabel("all", fontsize=12, rotation=270, labelpad=20)
ax1.yaxis.tick_right()
ax1.yaxis.set_label_position("right")
ax1.set_xlabel("day", fontsize=12)
ax2.set_ylabel(
    "proportion infected\n\nmisinformed", fontsize=12, rotation=270, labelpad=40
)
ax2.yaxis.tick_right()
ax2.yaxis.set_label_position("right")
ax2.set_xlabel("day", fontsize=12)
ax3.set_ylabel("ordinary", fontsize=12, rotation=270, labelpad=20)
ax3.yaxis.tick_right()
ax3.yaxis.set_label_position("right")
ax3.set_xlabel("day", fontsize=12)
ax5.set_ylabel("proportion of\nextra infections")
ax5.set_xlim(0, 10)

# Set x-tick fontsize to 12
for a in [ax1, ax2, ax3]:
    a.tick_params(axis="x", labelsize=12)
    a.tick_params(axis="y", labelsize=12)

# Remove x-axis ticks
# ax1.xaxis.set_ticklabels([])
# ax2.xaxis.set_ticklabels([])

# Use scalar values for x axis of ax5
ax5.xaxis.set_major_formatter(plt.ScalarFormatter())


# Ax 5
ax4 = plt.subplot(grid[0:2, 0])


frac_mis = 0.5
color_map = ["#4c78a8", "#f58518", "#e45756", "#72b7b2", "purple"]
for idx, beta in enumerate(totals_df.beta.unique()):
    temp_df = totals_df[(totals_df.beta == beta) & (totals_df.frac_mis == frac_mis)]
    ax4.plot(temp_df["lambda"], temp_df["total_inf"], label=beta, c=color_map[idx])
    # ax4.set_title(f"prop. misinformed = {frac_mis}", fontsize=10)


ax4.set_xlabel(r"$\lambda$")
# ax4.yaxis.tick_right()
# ax4.yaxis.set_label_position("right")
ax4.set_ylabel("proportion infected")
ax4.legend(
    title=r"$\beta_O$",
    ncols=3,
    frameon=False,
    loc="lower center",
    bbox_to_anchor=(0.5, 1),
)
ax4.set_xscale("log")

# format the xaxis tick values as scalar numbers
ax4.xaxis.set_major_formatter(plt.ScalarFormatter())

# remove spines on left and top
ax4.spines["top"].set_visible(False)
ax4.spines["right"].set_visible(False)
ax4.grid()

plt.subplots_adjust(wspace=0.15, hspace=0.5)

# Add subplot annotations
ax1.annotate(
    "(b)",
    xy=(-0.05, 1),
    xycoords=ax1.transAxes,
    fontsize=14,
    ha="center",
    va="center",
)
ax5.annotate(
    "(c)",
    xy=(-0.3, 1.2),
    xycoords=ax5.transAxes,
    fontsize=14,
    ha="center",
    va="center",
)

ax4.annotate(
    "(a)",
    xy=(-0.3, 1.0),
    xycoords=ax4.transAxes,
    fontsize=14,
    ha="center",
    va="center",
)

# # Save the plot
os.makedirs(OUT_DIR, exist_ok=True)
plt.savefig(os.path.join(OUT_DIR, "mf_lambda_effect.pdf"), bbox_inches="tight", dpi=800)
plt.savefig(
    os.path.join(OUT_DIR, "mf_lambda_effect.png"),
    bbox_inches="tight",
    dpi=800,
    transparent=True,
)
