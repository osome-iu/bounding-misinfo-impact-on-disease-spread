"""
Purpose:
    Generate the figure that shows the 3D effect of homophily on the misinformed group.

Inputs:
    None

Outputs:
    - figures_generation/mf_homophiliy_misinformed_effect_3d{mixed_str}.pdf
        mixed_str = "_mixed" if MIXED else "" (see code below)

Author:
    Matthew R. DeVerna
"""

import os

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

MIXED = True
OUT_DIR = "../figures"
CURR_DIR = "figures_generation"
RESULTS_DIR = "../sim_results/effects_of_homophily_on_misinformed"
# Ensure we are in the data_analysis directory for paths to work
if os.path.basename(os.getcwd()) != CURR_DIR:
    raise Exception(f"Must run this script from the `{CURR_DIR}` directory!")

MIXED = True
mixed_str = "_mixed" if MIXED else ""

daily_fname = os.path.join(RESULTS_DIR, f"daily_infected{mixed_str}.csv")
total_fname = os.path.join(RESULTS_DIR, f"total_infected{mixed_str}.csv")

daily_frame = pd.read_csv(daily_fname)
total_frame = pd.read_csv(total_fname)

column_name_map = {
    "total_ord_inf": "ordinary",
    "total_mis_inf": "misinformed",
    "total": "all",
}

fig = plt.figure(figsize=(12, 4))  # Adjust the figsize as needed
ax1 = fig.add_subplot(131, projection="3d")  # 1st subplot
ax2 = fig.add_subplot(132, projection="3d", sharez=ax1)  # 2nd subplot
ax3 = fig.add_subplot(133, projection="3d", sharez=ax1)  # 3rd subplot

column_ax_map = {"total_ord_inf": ax1, "total_mis_inf": ax2, "total": ax3}

for col in sorted(column_name_map.keys(), reverse=True):
    # Get our grid, based on the column
    reshaped_df = (
        total_frame[["alpha", "beta", col]]
        .round(2)
        .pivot(  # Rounding ensures a cleaner plot
            index="alpha", columns="beta", values=col
        )
    )

    if col in ["total_ord_inf", "total_mis_inf"]:
        reshaped_df = reshaped_df * 2

    # Select the proper axis to draw on and set labels
    temp_ax = column_ax_map[col]
    temp_ax.set_xlabel(r"$\alpha$")
    temp_ax.set_ylabel(r"$\beta_{O}$")
    temp_ax.set_zlabel("Prop. infected")
    temp_ax.set_title(column_name_map[col], pad=0)
    temp_ax.set_ylim((total_frame.beta.min(), total_frame.beta.max()))
    temp_ax.set_zlim((0, 1))

    # Create a mesh grid of alpha and beta values
    alpha_values = reshaped_df.index.values
    beta_values = reshaped_df.columns.values
    alpha_mesh, beta_mesh = np.meshgrid(alpha_values, beta_values)

    # Get the corresponding values as a 2D array
    prop_infected_values = reshaped_df.values

    # Create the figure
    temp_ax.plot_surface(
        alpha_mesh,
        beta_mesh,
        prop_infected_values.T,
        vmin=0,
        vmax=1,
        cmap="plasma",
    )

    if col == "total":
        max_points = []

        # Iterate through beta values
        for beta_value in reshaped_df.columns:
            # Find the row with the maximum z-value for this beta
            alpha = reshaped_df.loc[:, beta_value].idxmax()
            infected_prop = reshaped_df.loc[alpha, beta_value]
            max_points.append((alpha, beta_value, infected_prop))

        # Convert the list of maximum points to a NumPy array for plotting
        max_points = np.array(max_points)

        # Plot the maximum points as a scatter plot on the "all" subplot
        temp_ax.scatter(
            max_points[:, 0],
            max_points[:, 1],
            max_points[:, 2],
            color="black",
            marker=".",
            s=50,
            label="Max infection",
        )

# Control subplots spacing
plt.tight_layout()
plt.subplots_adjust(wspace=0.15)

# Add subplot annotations
ax1.annotate(
    "(a)",
    xy=(0.0, 0.95),
    xycoords=ax1.transAxes,
    fontsize=14,
    ha="center",
    va="center",
)

ax2.annotate(
    "(b)",
    xy=(0.0, 0.95),
    xycoords=ax2.transAxes,
    fontsize=14,
    ha="center",
    va="center",
)

ax3.annotate(
    "(c)",
    xy=(0.0, 0.95),
    xycoords=ax3.transAxes,
    fontsize=14,
    ha="center",
    va="center",
)

# Set y-axis ticks for all subplots
ticks = np.round(np.arange(0.1, 0.4, 0.1), 2)
ax1.yaxis.set_ticks(ticks, ticks)
ax2.yaxis.set_ticks(ticks, ticks)
ax3.yaxis.set_ticks(ticks, ticks)

# Create a colorbar for the entire figure
cbar = fig.colorbar(
    ax1.collections[0],
    ax=[ax1, ax2, ax3],
    location="bottom",
    shrink=0.2,
    ticks=np.linspace(0, 1, 2),
    pad=0.1,
)
cbar.set_label("Prop. infected", labelpad=-7)

# Save the plot
os.makedirs(OUT_DIR, exist_ok=True)
plt.savefig(
    os.path.join(OUT_DIR, f"mf_homophiliy_misinformed_effect_3d{mixed_str}.pdf"),
    dpi=800,
    bbox_inches="tight",
)
plt.savefig(
    os.path.join(OUT_DIR, f"mf_homophiliy_misinformed_effect_3d{mixed_str}.png"),
    dpi=800,
    bbox_inches="tight",
)
