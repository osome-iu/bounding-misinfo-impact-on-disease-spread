"""
Purpose: Mapping tweets, users, URLs and credibility score according to Newsguard

Input:
    - Daily files for:
        (dict) URL : list of tweet ids
        (dict) URL : URL_expanded
        (dict) user id : list of tweet ids
    - Global file with:
        (dict) user id : location

Output:
    - Global mappings:
       (dict) tweet id: {"domain": domain, "score": score} (created with map_tweet_score)
       (dict) tweet id : URL (created with map_tweet_url)
       (dict) account id : list of tweet ids shared (created with map_account_tweet)

Authors:
    - Francesco Pierri
    - Matthew DeVerna
"""
import os

import glob as glob
import pickle as pkl

from collections import defaultdict
from datetime import datetime as dt
from utils import parse_cl_args, parse_config_file

# This is needed for the eval(location) line to work below
from carmen.location import Location

LAST_DAY = "2021-09-30"


def map_tweet_score(config):
    """
    A function to map tweets to NG score of their URL (if present).

    Output dictionary:
    {
        tid1: {"domain": domain, "score": score},
        tid2: {"domain": domain, "score": score},
        ...
    }
    """

    tweet_source_score = dict()
    for file in sorted(
        glob.glob(config["PATHS"]["URLS_DAILY_FOLDER"] + "/*newsguard*")
    ):
        data = pkl.load(open(file, "rb"))
        for domain in data:
            for tid in data[domain]["tids"]:
                tweet_source_score[tid] = {
                    "domain": domain,
                    "score": data[domain]["ng_score"],
                }

    output_fp = os.path.join(
        config["PATHS"]["INTERMEDIATE_FILES"],
        config["FILES"]["TWEET_CREDIBILITY_SCORE"],
    )
    pkl.dump(
        tweet_source_score,
        open(
            output_fp,
            "wb",
        ),
    )


def map_tweet_url(config):
    """
    A function to map tweets to URLs shared.
    """

    last_day = dt.strptime(LAST_DAY, "%Y-%m-%d")

    tweet_url = dict()
    for file in sorted(glob.glob(config["PATHS"]["URLS_DAILY_FOLDER"] + "/*_urls.pkl")):
        day = os.path.basename(file).replace("_urls.pkl", "")
        day = dt.strptime(day, "%Y-%m-%d")

        if day > last_day:
            break

        # Load all URLs for that day
        urls_tweet_match = pkl.load(open(file, "rb"))

        # Need to get expanded domains, if present
        urls_expanded_dict = pkl.load(
            open(file.replace("_urls.pkl", "_urls_expanded.pkl"), "rb")
        )

        # Add the tid -> URL mapping, use full URL if shortened
        for u, tids in urls_tweet_match.items():
            # If the URL is shortened, take expanded version
            if u in urls_expanded_dict:
                full_url = urls_expanded_dict[u]
            else:
                full_url = u
            for t in tids:
                tweet_url[t] = full_url

    output_fp = os.path.join(
        config["PATHS"]["INTERMEDIATE_FILES"], config["FILES"]["TWEET_URL"]
    )
    pkl.dump(
        tweet_url,
        open(
            output_fp,
            "wb",
        ),
    )


def map_account_tweet(config):
    """
    A function to map accounts to tweet ids shared
    """
    account_tweet = defaultdict(list)

    last_day = dt.strptime(LAST_DAY, "%Y-%m-%d")

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

    print("Done building `account_county`.")

    ## Loading daily files with "account <-> tweet" dictionary
    for file in sorted(
        glob.glob(os.path.join(config["PATHS"]["URLS_DAILY_FOLDER"], "*_urls.pkl"))
    ):
        print(file)
        day = os.path.basename(file).replace("_urls.pkl", "")

        # Convert to dt for date check
        day = dt.strptime(day, "%Y-%m-%d")
        if day > last_day:
            break

        # Convert back for file name building
        day = os.path.basename(file).replace("_urls.pkl", "")

        daily_account_tweet = pkl.load(
            open(
                os.path.join(
                    config["PATHS"]["ACCOUNTS_DATA_FOLDER"],
                    str(day) + "_account_tids_dict.pkl",
                ),
                "rb",
            )
        )

        # a bit unnecessary but to be 100% sure we are working with strings here
        for k in list(daily_account_tweet.keys()):
            daily_account_tweet[str(k)] = daily_account_tweet[k]

        # only geolocated accounts
        for a in account_county:
            if a in daily_account_tweet:
                account_tweet[a] += daily_account_tweet[a]

    pkl.dump(
        account_tweet,
        open(
            os.path.join(
                config["PATHS"]["INTERMEDIATE_FILES"], config["FILES"]["ACCOUNT_TWEETS"]
            ),
            "wb",
        ),
    )


if __name__ == "__main__":
    try:
        # Load the config file variables
        args = parse_cl_args()
        config = parse_config_file(args.config_file)

        print("Map tweets to NG score.")
        map_tweet_score(config)

        print("Map tweets to URLs.")
        map_tweet_url(config)

        print("Map tweets to accounts.")
        map_account_tweet(config)
    except Exception as e:
        print("Something's wrong.")
        print(e)
        exit(1)
