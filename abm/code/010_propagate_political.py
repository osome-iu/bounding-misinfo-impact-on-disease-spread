"""
Purpose: Propagate the political scores of users within our Twitter network
    to their neighbors. We assume some degree of homophily, so that we can
    (for users without their own estimated political ideology) take the average
    estimated ideology of all their neighbors.

Input:
    - Global retweeting network
        - Nodes are users and directed edges indicate the direction of
        information flow. I.e., if an edge is drawn from user i to user j,
        this indicates that user j retweeted user i. The edge weight represents
        the number of times each user retweeted one another.
    - Dictionary containing the est. ideological score for all URLs shared by
        all users.
        - Form: {user_id : [list of scores between -1 and +1]}
            where each score represents the ideological est. of a domain
            shared by user_id
    - User Account Table
        - Includes the estimated ideology of users. Each row represents
            an individual user.

Output:
    - An updated Account Table inclusive of the users that we
        propagated ideology scores to.

Authors:
    - Francesco Pierri
    - Matthew DeVerna
"""
import os

import networkx as nx
import numpy as np
import pandas as pd
import pickle as pkl

from utils import parse_cl_args, parse_config_file


def propagate_political(config):
    """
    Propagate the political scores of users whom we have an estimated ideology
    score to their neighbors, then update the table.
    """

    # Load global retweeting network
    #   Nodes are users and directed edges indicate the direction
    #   of information flow.
    g = nx.read_gexf(
        os.path.join(
            config["PATHS"]["INTERMEDIATE_FILES"],
            config["FILES"]["GLOBAL_RETWEETING_GRAPH"],
        )
    )

    # Load dictionary containing the est. ideological score for all
    # URLs shared by all users.
    #   Form: {user_id : [list of scores between -1 and +1]}
    account_political = pkl.load(
        open(
            os.path.join(
                config["PATHS"]["INTERMEDIATE_FILES"],
                config["FILES"]["ACCOUNT_POLITICAL"],
            ),
            "rb",
        )
    )

    # Calculate the mean ideological score for each user in the network.
    # Note: this is only done if users shared domains for which we have
    # ideological estimates
    user_count = 0
    for n in g.nodes:
        if n in account_political:
            # `account_political[n]` is an array of scores, one for each URL shared
            g.nodes[n]["political_mean"] = np.mean(account_political[n])
            user_count += 1
    print("Nodes with political score: " + str(user_count))

    # Now we propogate the scores we already have to other
    # users in the network. To do this, we assume the network
    # is undirected.

    g = nx.to_undirected(g)

    # This flag makes the while loop continue to run as long as at
    # least one node gets a propagated political score.
    loop_flag = 0
    while loop_flag == 0:
        print("Updated no. nodes with score: " + str(user_count))

        # Flip the flag to exit the while loop
        loop_flag = 1

        for u in g.nodes:
            neighbors_score = []

            # This flag is used to ensure that ideology is propagated only if
            # ALL neighbors have a political score
            node_flag = 1

            # Only attempt to propagate a political score if we don't have one already
            if "political_mean" not in g.nodes[u]:
                for edge in g.edges(u):
                    v = edge[1]  # edge = (u,v)
                    if v == u:  # ignore self loops
                        continue

                    # If any of the nieghbors do not have a political score
                    # then we don't propagate ideology estimates
                    # (with node_flag = 0; see below)
                    if "political_mean" not in g.nodes[v]:
                        node_flag = 0
                        break

                    # Add the political score the same number of times as
                    # the weighted average. This way we can calculate the
                    # weighted average below by taking the mean of this array
                    weight = int(g.edges[edge]["weight"])
                    neighbors_score += [
                        g.nodes[v]["political_mean"] for _ in range(weight)
                    ]

            # Boolean checks to control whether we propagate scores
            have_neighb_scores = len(neighbors_score) > 0
            all_neighbs_have_scores = node_flag == 1

            if have_neighb_scores and all_neighbs_have_scores:
                g.nodes[u]["political_mean"] = np.mean(neighbors_score)

                # We've propagated at least one political score, so the
                # loop_flag is set to 0 so that we loop the nodes again
                loop_flag = 0
                user_count += 1

    # Load .csv that contains information for all users
    #   Form:
    #   - Each rows represents an individual user_id
    #   - Columns include details like ideological estimate
    pre_df = pd.read_csv(
        os.path.join(
            config["PATHS"]["INTERMEDIATE_FILES"], config["FILES"]["ACCOUNT_TABLE"]
        )
    )

    post_df = pre_df.copy()

    # Now we take the new values, where present, and add them to the table
    post_political_values = []
    for ix, row in post_df.iterrows():
        account_id = str(row["account_id"])

        # The table contains more accounts than the graph because the graph contains
        # only users retweeting other users. When the account is not present in the graph,
        # we just take their existing value.
        if account_id not in g.nodes:
            post_political_values.append(row["political_score"])
            continue

        # If we have a political value for users in our network we include that
        # in the table. Otherwise, we include np.NaN
        post_political = (
            g.nodes[account_id]["political_mean"]
            if "political_mean" in g.nodes[account_id]
            else np.NaN
        )
        post_political_values.append(post_political)
    post_df["political_score"] = post_political_values

    # Create a new post-propagation user account table
    post_df.to_csv(
        os.path.join(
            config["PATHS"]["INTERMEDIATE_FILES"],
            config["FILES"]["ACCOUNT_TABLE_PROPAGATED"],
        ),
        index=False,
    )


if __name__ == "__main__":
    try:
        # Load the config file variables
        args = parse_cl_args()
        config = parse_config_file(args.config_file)

        print("Propagate political score based on the global retweeting graph.")
        propagate_political(config)
        exit(0)
    except Exception as e:
        print(e)
        print("Something's wrong.")
        exit(1)
