"""
Purpose:
    Run one step of the linear threshold opinion spreading dynamics on a retweeting
    graph of geolocated Twitter users within the United States.

Input:
    - All inputs derived from the project config.ini file which is input with
        the '-c' flag.
    - What is utilized in the script is a .gexf graph with node-level attributes
        and some parameters for the algorithm.

Output:
    - LT_output.pkl
        - A pickle file containing a set of nodes that have been marked as
            misinformed, at each linear threshold level.
        - Keys represent the LT threshold level.
        - Values represent a set of nodes that have been marked as misinformed.

Authors:
    - Francesco Pierri
    - Matthew DeVerna
"""
import os

import networkx as nx
import numpy as np
import pickle as pkl

from copy import deepcopy
from collections import defaultdict
from utils import parse_cl_args, parse_config_file


class OpinionDynamicsGraph:
    """
    A class for running opinion dynamics on networkx graphs.
    """

    def __init__(self, graph):
        self._graph = graph

    def run_LT(self, threshold, opinion_variable_name="NG < 60"):
        """
        Use a Linear Threshold model to propagate misinformation to other nodes. Note, node opinions
        are updated in place.

        How the algorithm works:
        - Each node is assigned a binary misinformation status which is 1 if misinformation
            (i.e., 'opinion_variable_name') > 0, else 0.
        - A threshold is set beforehand that determines how many neighbors must be misinformed
            for a non-misinformed individual to become misinformed.
        - Then, for all nodes with opinion values != 1, we check the number of misinformed neighbors
            (in-edges only). If the number of neighbors is >= the threshold, this node is added
            to a list of nodes whos opinion values will be updated at the end of the process
            when their misinformed status is set to 1.
        - Keeping a separate list of new nodes ensures that the spreading does not go beyond a
            single step.

        Parameters:
        ----------
        - threshold (int): The threshold at which we flip misinformed status.
        - opinion_variable_name (str) : the node attribute that we check to see if a node shared
            misinformation. The values in this attribute represent the number of times that a node
            shared a low-cred article as determined by NewsGuard, given different thresholds.

        Returns:
        ---------
        - Nothing is returned. Graph node opinions are updated in place.
        """
        # Check input types
        if not isinstance(opinion_variable_name, str):
            raise TypeError("`opinion_variable_name` must be of type `str`")

        graph = self._graph

        # Set the opinion of nodes who have shared any low-cred articles to 1
        nodes = list(graph.nodes)
        num_initial_mis_nodes = 0
        for node in nodes:
            if graph.nodes[node][opinion_variable_name] > 0:
                graph.nodes[node]["opinion"] = 1
                num_initial_mis_nodes += 1
            else:
                graph.nodes[node]["opinion"] = 0
        print(f"Initial misinformed nodes: {num_initial_mis_nodes:,}")

        # Update opinion values based on neighbors and the `threshold`
        misinformed_nodes = set()
        for node in nodes:
            # Node is already misinformed so we can skip
            if graph.nodes[node]["opinion"] == 1:
                continue

            # Get list of incoming edges
            in_edges = list(graph.in_edges(node))

            num_bad_neighbors = 0
            for edge in in_edges:
                neighb = edge[0]

                # Skip self loops
                if neighb == node:
                    continue

                # Get this neighbor opinion
                neighb_opinion = graph.nodes[neighb]["opinion"]

                # Count bad neighbors
                if neighb_opinion == 1:
                    num_bad_neighbors += 1

            # If they meet the threshold, save this node to update later
            if num_bad_neighbors >= threshold:
                misinformed_nodes.add(node)

        # Update misinformed nodes with opinion 1 in the actual graph
        print(f"Number of new misinformed nodes: {len(misinformed_nodes):,}")
        for node in misinformed_nodes:
            graph.nodes[node]["opinion"] = 1


if __name__ == "__main__":
    try:
        # Load the config file variables
        args = parse_cl_args()
        config = parse_config_file(args.config_file)
        output_file_name = config["FILES"]["LT_OUTPUT"]

        print("Loading global retweeting graph attributed.")
        original_graph = nx.read_gexf(
            os.path.join(
                config["PATHS"]["INTERMEDIATE_FILES"],
                config["FILES"]["GLOBAL_RETWEETING_GRAPH_ATTRIBUTED"],
            )
        )

        print(
            "Running LT model on the global retweeting "
            "graph with different thresholds."
        )
        threshold_new_nodes = defaultdict(set)

        # Set some helpful update messages for the loop
        threshold_msg = "Running opinion spreading dynamics with threshold :"
        mis_nodes_msg = "\t- Number of misinformed nodes after spreading :"

        # Set thresholds
        thresholds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 75, 100]

        print("Linear threshold dynamics based on number of misinformed neighbors")
        print(f"Simulating spread for {len(thresholds)} threshold levels.")
        print("They are:")
        for idx, thresh in enumerate(thresholds, start=1):
            print(f"\t- {idx}. {thresh}")

        for threshold in thresholds:
            print(threshold_msg, np.round(threshold, 2))

            temp_graph = deepcopy(original_graph)
            ODG = OpinionDynamicsGraph(temp_graph)
            ODG.run_LT(threshold=threshold)

            print("Storing misinformed nodes at this threshold...")
            for node in ODG._graph.nodes:
                if ODG._graph.nodes[node]["opinion"] == 1:
                    threshold_new_nodes[threshold].add(node)

            print(mis_nodes_msg, f"{len(threshold_new_nodes[threshold]):,}\n")

        print("Saving new nodes for each threshold.")
        output_file_path = os.path.join(
            config["PATHS"]["INTERMEDIATE_FILES"], output_file_name
        )
        pkl.dump(threshold_new_nodes, open(output_file_path, "wb"))
        print("--- Script complete ---")

    except Exception as e:
        print(e)
        print("Something's wrong.")
