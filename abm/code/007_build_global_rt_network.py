"""
Purpose: Create a global directed weighted retweeting network for users
    geolocated in US counties.

Input:
    - Files with retweeting edges for each day (tables in .parquet format)
    - Tweet IDs mapped to NewsGuard domain and credibility scores
    - 


Output:
    1. A list of retweeting edges with time, website and Newsguard score (if URL is present in the tweet):
        - Columns: | RTed_id | RTing_id | tweet_id | time | domain | NG_score |
    2. A weighted directed graph in .gexf format

    - Both of the above represent a "global retweet network" for all accounts
        that we identified as being in a US county.

Authors:
    - Francesco Pierri
    - Matthew DeVerna
"""
import os

import datetime as datetime
import glob as glob
import pickle as pkl
import pandas as pd
import networkx as nx

from datetime import datetime as dt
from utils import parse_cl_args, parse_config_file

# This is needed for the eval(location) line to work below
from carmen.location import Location

LAST_DAY = "2021-09-30"


def build_global_edges(config):
    """
    A function to read daily retweeting networks and aggregate them in a unique list of edges.
    Columns in the output:
    | RTed_id | RTing_id | tweet_id | time | domain | NG_score |
    """
    edges = []

    last_day = dt.strptime(LAST_DAY, "%Y-%m-%d")

    # Newsguard score for each tweet containing URLs
    tweet_source_score = pkl.load(
        open(
            os.path.join(
                config["PATHS"]["INTERMEDIATE_FILES"],
                config["FILES"]["TWEET_CREDIBILITY_SCORE"],
            ),
            "rb",
        )
    )

    # Checking geolocated accounts
    location_match = pkl.load(
        open(
            os.path.join(
                config["PATHS"]["INTERMEDIATE_FILES"],
                config["FILES"]["ACCOUNT_LOCATION"],
            ),
            "rb",
        )
    )
    account_county = dict()
    for key in location_match:
        acc = location_match[key]

        if not acc["location"]:  # no location, skip
            continue

        key = str(key)  # to ensure consistency

        location = acc["carmen_location"]
        if location == "No match!":
            continue
        # check if it's U.S.
        location = eval(location)  # use Carmen Location object
        if location.country == "United States" and location.state and location.county:
            county = location.county
            state = location.state
            account_county[key] = [county, state]

    for file in sorted(
        glob.glob(config["PATHS"]["RETWEET_NETWORK_FOLDER"] + "/*edgelist*")
    ):
        day = (
            os.path.basename(file)
            .replace(".parquet", "")
            .replace("retweets_edgelist_", "")
        )

        print(day)

        day = dt.strptime(day, "%Y-%m-%d")

        if day > last_day:
            break

        df = pd.read_parquet(file)
        df["retweeting_user_id"] = df["retweeting_user_id"].astype(str)
        df["retweeted_user_id"] = df["retweeted_user_id"].astype(str)

        ## Filtering US-counties accounts
        df = df[
            (df["retweeting_user_id"].isin(account_county))
            & (df["retweeted_user_id"].isin(account_county))
        ]

        ## Adding domain and score for Newsguard sources link
        df["tweet_id"] = df["tweet_id"].astype(str)
        df["domain"] = [
            tweet_source_score[tid]["domain"] if tid in tweet_source_score else None
            for tid in df["tweet_id"]
        ]
        df["score"] = [
            tweet_source_score[tid]["score"] if tid in tweet_source_score else -1
            for tid in df["tweet_id"]
        ]

        edges.append(df)
    edges = pd.concat(edges)

    edges.to_csv(
        os.path.join(
            config["PATHS"]["INTERMEDIATE_FILES"],
            config["FILES"]["GLOBAL_RETWEETING_EDGES"],
        ),
        index=False,
    )


def build_global_graph(config):
    """
    A function to read the global list of edges and create a .gexf graph
    """

    df = pd.read_csv(
        os.path.join(
            config["PATHS"]["INTERMEDIATE_FILES"],
            config["FILES"]["GLOBAL_RETWEETING_EDGES"],
        )
    )

    g = nx.DiGraph()
    for ix, row in df.iterrows():
        a = row["retweeted_user_id"]
        b = row["retweeting_user_id"]

        if g.has_edge(a, b):
            g.edges[(a, b)]["weight"] += 1
        else:
            g.add_edge(a, b, weight=1)

    nx.write_gexf(
        g,
        os.path.join(
            config["PATHS"]["INTERMEDIATE_FILES"],
            config["FILES"]["GLOBAL_RETWEETING_GRAPH"],
        ),
    )


if __name__ == "__main__":
    try:
        # Load the config file variables
        args = parse_cl_args()
        config = parse_config_file(args.config_file)

        print("Build global list of rt edges.")
        build_global_edges(config)

        print("Build .gexf graph.")
        build_global_graph(config)
        exit(0)
    except Exception as e:
        print(e)
        print("Something's wrong.")
        exit(1)
