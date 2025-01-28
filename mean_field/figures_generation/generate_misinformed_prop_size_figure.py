"""
Purpose:
    Generate the figure that shows the proportion of the network that becomes infected
    as a function of the size of network that is misinformed, by beta value, specifically
    for lambda = 100.

Inputs:
    None

Outputs:
    - figures_generation/generate_misinformed_prop_size_figure.py

Author:
    Matthew R. DeVerna
"""

import os
import sys

import matplotlib.pyplot as plt
import pandas as pd


### Load simulation results ###
totals_df = pd.read_csv(
    os.path.join("../sim_results/effects_of_lambda", "total_infected_all_settings.csv")
)
by_day_df = pd.read_csv(
    os.path.join("../sim_results/effects_of_lambda", "daily_infected_all_settings.csv")
)


OUT_DIR = "../figures"
CURR_DIR = "figures_generation"
RESULTS_DIR = "../sim_results/effects_of_lambda"
# Ensure we are in the data_analysis directory for paths to work
if os.path.basename(os.getcwd()) != CURR_DIR:
    raise Exception(f"Must run this script from the `{CURR_DIR}` directory!")

### Load simulation results ###
totals_df = pd.read_csv(os.path.join(RESULTS_DIR, "total_infected_all_settings.csv"))
lambda_100 = totals_df[totals_df["lambda"] == 100]

# Specify some plotting parameters
beta_vals = [0.001, 0.01, 0.1, 0.2, 0.3]
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
color_map = {val: color_list[idx] for idx, val in enumerate(beta_vals)}
line_map = {
    0.001: "dotted",
    0.01: "dashed",
    0.1: "solid",
    0.2: "dashdot",
    0.3: (0.5, (1, 5)),
}

fig, ax = plt.subplots(ncols=2, figsize=(10, 4))

ax1 = ax[0]
ax2 = ax[1]

beta_vals = [0.001, 0.01, 0.1, 0.2, 0.3]
color_map = {val: color_list[idx] for idx, val in enumerate(beta_vals)}
line_map = {
    0.001: "dotted",
    0.01: "dashed",
    0.1: "solid",
    0.2: "dashdot",
    0.3: (0.5, (1, 5)),
}

# Plotting for ax1
for idx, beta in enumerate(beta_vals):
    beta_df = lambda_100[lambda_100["beta"] == beta]
    ax1.plot(
        beta_df["frac_mis"],
        beta_df["total_inf"],
        label=beta,
        c=color_list[idx],
        linestyle=line_map[beta],
        marker=".",
    )

ax1.set_xscale("log")
ax1.set_xticks(
    ticks=lambda_100["frac_mis"].unique(),
    labels=[
        f"{x:.3f}" if x < 1 else f"{int(x)}" for x in lambda_100["frac_mis"].unique()
    ],
    rotation=90,
    fontsize=10,
)
ax1.set_ylabel("proportion of network infected")
ax1.set_xlim(0.0005, 1)
ax1.grid(axis="y")
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)

# Plotting for ax2
for idx, beta in enumerate(beta_vals):
    temp_df = lambda_100[lambda_100["beta"] == beta]
    ax2.plot(
        temp_df["frac_mis"],
        temp_df["r0"],
        label=beta,
        c=color_list[idx],
        linestyle=line_map[beta],
        marker=".",
    )

ax2.set_xscale("log")
ax2.xaxis.set_major_formatter(plt.ScalarFormatter())
ax2.set_xticks(
    ticks=lambda_100["frac_mis"].unique(),
    labels=[
        f"{x:.3f}" if x < 1 else f"{int(x)}" for x in lambda_100["frac_mis"].unique()
    ],
    rotation=90,
    fontsize=10,
)
ax2.set_ylabel(r"$R_0$")
ax2.axhline(y=1, color="black", linestyle="--")
ax2.grid(axis="y")
# Set y-axis to the right for ax2
# ax2.yaxis.tick_right()
# ax2.yaxis.set_label_position("right")

ax2.spines["top"].set_visible(False)
# ax2.spines["left"].set_visible(False)
ax2.spines["right"].set_visible(False)

fig.supxlabel("proportion of population misinformed", x=0.5, y=-0.1, fontsize=12)

ax2.legend(
    ncol=5,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.05),
    frameon=False,
    title=r"$\beta_O$",
    bbox_transform=fig.transFigure,
)

plt.subplots_adjust(wspace=0.3)

ax1.annotate(
    "(a)",
    xy=(-0.2, 1.0),
    xycoords=ax1.transAxes,
    fontsize=14,
    ha="center",
    va="center",
)
ax2.annotate(
    "(b)",
    xy=(-0.12, 1.0),
    xycoords=ax2.transAxes,
    fontsize=14,
    ha="center",
    va="center",
)

plt.savefig(
    os.path.join("../figures", "mf_misinformed_prop_size_w_beta_effect.pdf"),
    dpi=800,
    bbox_inches="tight",
)
plt.savefig(
    os.path.join("../figures", "mf_misinformed_prop_size_w_beta_effect.png"),
    dpi=800,
    bbox_inches="tight",
    transparent=True,
)
