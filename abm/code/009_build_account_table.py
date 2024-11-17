"""
Purpose:
    - Create an account table that includes location, estimated ideology score,
        and percentage of misinformation shared by individual user.

Input:
    - Carmen location data dictionary
    - Account tweet_ids dictionary
    - Tweet URL credibility rating dictionary
    - Political estimates of users

Output:
    - A single .csv with the following information.
        - Location (As identified by the Carmen package)
        - Estimated political ideology score
        - Percent of misinformation shared

Authors:
    - Francesco Pierri
    - Matthew DeVerna
"""
import os
import csv

import pickle as pkl
import numpy as np

from collections import Counter
from utils import parse_cl_args, parse_config_file

# This is needed for the eval(location) line to work below
from carmen.location import Location


def get_account_table(config):
    """
    Create an account-specific dataframe with location, political score and % misinformation
    """

    # Load {User:Location} dictionary
    #   Locations found with Carmen package
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
        acc_obj = location_match[key]

        if not acc_obj["location"]:  # no location, skip
            continue

        acc_key = str(key)  # to ensure consistency with nodes and account ids

        location = acc_obj["carmen_location"]
        if location == "No match!":
            continue
        # check if it's U.S.
        location = eval(location)  # use Carmen Location object
        if location.country == "United States" and location.state and location.county:
            county = location.county
            state = location.state
            account_county[acc_key] = [county, state]

    print("Loaded locations.")

    account_tweet = pkl.load(
        open(
            os.path.join(
                config["PATHS"]["INTERMEDIATE_FILES"], config["FILES"]["ACCOUNT_TWEETS"]
            ),
            "rb",
        )
    )
    print("Loaded account->tweet mapping.")

    # credibility
    tweet_source_score = pkl.load(
        open(
            os.path.join(
                config["PATHS"]["INTERMEDIATE_FILES"],
                config["FILES"]["TWEET_CREDIBILITY_SCORE"],
            ),
            "rb",
        )
    )
    print("Loaded tweet->credibility mapping.")

    # political
    account_political = pkl.load(
        open(
            os.path.join(
                config["PATHS"]["INTERMEDIATE_FILES"],
                config["FILES"]["ACCOUNT_POLITICAL"],
            ),
            "rb",
        )
    )
    print("Loaded account->political score mapping.")

    ng_thresholds = [10, 20, 30, 40, 50, 60]

    ## Manually writing .csv file for the table
    filepath = os.path.join(
        config["PATHS"]["INTERMEDIATE_FILES"], config["FILES"]["ACCOUNT_TABLE"]
    )
    with open(filepath, "w", newline="") as csvfile:
        # Construct the header/columns and write them
        fieldnames = ["account_id", "state", "county", "political_score"]
        fieldnames += ["NG < " + str(threshold) for threshold in ng_thresholds]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",")
        writer.writeheader()

        for account_id in account_tweet:
            ### Determine account's political score ###
            # ------------------------------------- ###

            # If no location, we skip
            if account_id not in account_county:
                continue
            # Must have at shared at least one URL with estimated political score
            if account_political[account_id]:
                political_score = np.mean(account_political[account_id])
            # If not, score is NaN
            else:
                political_score = np.NaN

            ### Determine the percentage of tweets shared that     ###
            ### are low-credibility, given different NG thresholds ###
            # ---------------------------------------------------- ###
            misinfo_fraction = dict()
            misinfo_no_tweets = Counter()

            # Iterate through all tweets sent by the account
            for tid in account_tweet[account_id]:
                if tid in tweet_source_score:
                    score = tweet_source_score[tid]["score"]

                    # Skip tweets with no credibility score
                    if not np.isfinite(tweet_source_score[tid]["score"]):
                        continue

                    # Count the number of tweets for each NG threshold
                    for ng_threshold in ng_thresholds:
                        if score < ng_threshold:
                            misinfo_no_tweets[ng_threshold] += 1

            # Calculate the percentage of low-cred tweets, relative to all tweets
            # sent by the account, for each NG threshold
            num_tweets = len(account_tweet[account_id])
            for ng_threshold in ng_thresholds:
                misinfo_fraction[ng_threshold] = (
                    misinfo_no_tweets[ng_threshold] / num_tweets
                )

            ### Write a single row to the .csv file ###
            # ------------------------------------- ###

            # We are using the csv.DictWriter which takes dictionaries as input.

            data = dict()
            data["account_id"] = account_id
            data["county"] = account_county[account_id][0]
            data["state"] = account_county[account_id][1]
            data["political_score"] = political_score
            for threshold in misinfo_fraction:
                data["NG < " + str(threshold)] = misinfo_fraction[threshold]
            writer.writerow(data)


if __name__ == "__main__":
    try:
        # Load the config file variables
        args = parse_cl_args()
        config = parse_config_file(args.config_file)

        print("Get a table of statistics for each geolocated account.")
        get_account_table(config)
        exit(0)

    except Exception as e:
        print(e)
        exit(1)
