"""
Purpose: Create a weighted directed retweeting graph in .gexf format with node-level attributes

Input:
    - Global retweeting graph
    - Table of propagated account information

Output:
    - A single .gexf with attributes at the node level (county, political score, misinformation)

Authors:
    - Francesco Pierri
    - Matthew DeVerna
"""
import os

import networkx as nx
import numpy as np
import pandas as pd

from utils import parse_cl_args, parse_config_file

# NG attributes represent the % of shared tweets that
# are low credibility given different NG thresholds.
# E.g., threshold at NG score of 60 = NG < 60
ATTRIBUTES = [
    "county",
    "state",
    "political_score",
    "NG < 10",
    "NG < 20",
    "NG < 30",
    "NG < 40",
    "NG < 50",
    "NG < 60",
]


def build_global_graph_attributed(config):
    """
    A function to read account table (after propagation of political scores) and global retweeting graph, and it outputs a graph with attributes.
    """

    # Load the old graph and the table that contains the attributes
    g = nx.read_gexf(
        os.path.join(
            config["PATHS"]["INTERMEDIATE_FILES"],
            config["FILES"]["GLOBAL_RETWEETING_GRAPH"],
        )
    )
    table = pd.read_csv(
        os.path.join(
            config["PATHS"]["INTERMEDIATE_FILES"],
            config["FILES"]["ACCOUNT_TABLE_PROPAGATED"],
        )
    )

    # Update the graph with attributes
    for ix, row in table.iterrows():
        for key in ATTRIBUTES:
            account_id = str(row["account_id"])
            if account_id not in g.nodes:
                continue
            g.nodes[account_id][key] = row[key]

    # Remove nodes without political score
    for n in list(g.nodes):
        if np.isnan(g.nodes[n]["political_score"]):
            g.remove_node(n)

    # Save the graph
    nx.write_gexf(
        g,
        os.path.join(
            config["PATHS"]["INTERMEDIATE_FILES"],
            config["FILES"]["GLOBAL_RETWEETING_GRAPH_ATTRIBUTED"],
        ),
    )


if __name__ == "__main__":
    try:
        # Load the config file variables
        args = parse_cl_args()
        config = parse_config_file(args.config_file)

        print("Build global .gexf graph with node attributes.")
        build_global_graph_attributed(config)
        exit(0)
    except Exception as e:
        print(e)
        print("Something's wrong.")
        exit(1)
