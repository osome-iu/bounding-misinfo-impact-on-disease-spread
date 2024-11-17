"""
Purpose: Extract locations from accounts for each day of Twitter data, 
and it maps each user to its location and the set of tweet ids shared on each day.
It also combines all location in a unique mapping from user to location.

Input:
    - Files with tweets collected for each day (.json.gz format)

Output:
    1) account_tid_location_match:
    - A dictionary, for each day, with a mapping from account id to tweet ids
        - Form (dict): {user_id : [tweet_id]}
        - Form (dict): {user_id : location}
    2) "Global" account_id -> location dictionary:
        - Dictionary mapping account id to location for all days
            - Uses the last appearing location

Authors:
    - Francesco Pierri
    - Matthew DeVerna
"""
import gzip
import json
import os
import tldextract

import pickle as pkl
import glob as glob

from carmen import get_resolver
from collections import defaultdict
from datetime import datetime as dt

from utils import parse_cl_args, parse_config_file


def extract_top_domain(url):
    """
    Extract the top-level domain of a given URL

    Parameters:
    ----------
    url (str): URL to extract the top-level domain from

    Returns:
    -------
    str: Top-level domain of the URL guaranteed to be lowercase
    """
    extraction_result = tldextract.extract(url)
    domain = extraction_result.domain
    suffix = extraction_result.suffix
    return f"{domain}.{suffix}".lower()


## This function runs on the CoVaxxy dataset streaming files ##
# See dataset paper here: https://doi.org/10.1609/icwsm.v15i1.18122
# Tweet IDs can be found here for rehydration: https://zenodo.org/records/7752586
def account_tid_location_match(config):
    """
    Function to match tweets with accounts (and their locations). It processes daily Twitter files and checks for existing
    output to avoid repeating computations.
    Parameters:
        config (dict): A dictionary with config information about paths and filenames.
    Output:
        1) It saves a dictionary {'account_id' : [tweet_id]} which contains the list of tweets shared by each account on
        each day
        2) It saves a dictionary {'account_id' : {'location': str, 'carmen_location': str} } which contains the location
         of each account (and the carmen match) on each day
    """

    # Initialize carmen geolocation
    resolver = get_resolver()
    resolver.load_locations()

    sorted_files = sorted(
        glob.glob(config["PATHS"]["STREAMING_FILES_FOLDER"] + "/*json.gz*")
    )
    for file in sorted_files:
        path_front = config["PATHS"]["STREAMING_FILES_FOLDER"] + "/streaming_data--"
        path_back = ".json.gz"
        day = file.replace(path_front, "").replace(path_back, "")
        print(day)

        output_path = os.path.join(
            config["PATHS"]["ACCOUNTS_DATA_FOLDER"], str(day) + "_account_tids_dict.pkl"
        )
        if os.path.exists(output_path):
            print("Already processed!")
            continue

        daily_account_tweet_ids = defaultdict(list)
        daily_account_location_match = defaultdict(dict)

        with gzip.open(file, "r") as f:
            for line in f:
                try:
                    j = json.loads(line)
                    a_id = j["user"]["id"]

                    # append tweets shared in that day
                    daily_account_tweet_ids[a_id].append(j["id_str"])
                    account = j["user"]
                    aid = account["id"]

                    daily_account_location_match[aid] = {
                        "location": account["location"]
                    }

                    # trick to use carmen
                    result = resolver.resolve_tweet({"user": account})
                    if not result:
                        match = "No match!"
                    else:
                        # result[1] is a Location() object. E.g.
                        #       Location(
                        #           country='United Kingdom',
                        #           state='England',
                        #           county='London',
                        #           city='London',
                        #           known=True,
                        #           id=2206
                        #       )
                        match = str(result[1])

                    daily_account_location_match[aid]["carmen_location"] = match

                except Exception as e:
                    print(e)
                    print(j)

        pkl.dump(
            daily_account_tweet_ids,
            open(
                output_path,
                "wb",
            ),
        )
        pkl.dump(
            daily_account_location_match,
            open(
                os.path.join(
                    config["PATHS"]["ACCOUNTS_DATA_FOLDER"],
                    str(day) + "_account_location_match.pkl",
                ),
                "wb",
            ),
        )


## This is specific to this project ##
def build_global_location(config):
    """
    Function to build a global dictionary account -> location (the last appearing is retained).
    """

    # Cutoff date. We do not consider streaming data files after this date.
    LAST_DAY = config["VARIABLES"]["LAST_DAY"]
    LAST_DAY = dt.strptime(LAST_DAY, "%Y-%m-%d")

    account_location_match = dict()
    files_sorted = sorted(
        glob.glob(config["PATHS"]["RETWEET_NETWORK_FOLDER"] + "/*edgelist*")
    )
    for file in files_sorted:
        day = (
            os.path.basename(file)
            .replace("retweets_edgelist_", "")  # Strip front
            .replace(".parquet", "")  # Strip back
        )
        print(day)

        # Checking geolocated accounts in each day
        location_match = pkl.load(
            open(
                os.path.join(
                    config["PATHS"]["ACCOUNTS_DATA_FOLDER"],
                    day + "_account_location_match.pkl",
                ),
                "rb",
            )
        )

        day = dt.strptime(day, "%Y-%m-%d")

        if day > LAST_DAY:
            break

        for key in location_match:
            account_location_match[key] = location_match[key]

    pkl.dump(
        account_location_match,
        open(
            os.path.join(
                config["PATHS"]["INTERMEDIATE_FILES"],
                config["FILES"]["ACCOUNT_LOCATION"],
            ),
            "wb",
        ),
    )


if __name__ == "__main__":
    try:
        # Load the config file variables
        args = parse_cl_args()
        config = parse_config_file(args.config_file)

        print("Extracting locations from daily files.")
        account_tid_location_match(config)

        print("Putting everything together in a unique dictionary.")
        build_global_location(config)
        exit(0)

    except Exception as e:
        print(e)
        print("Something's wrong.")
        exit(1)
