"""
Purpose: Create retweet networks from CoVaxxy streaming data.

Input: A configuration file (.ini) which points to relevant folders and files.

Notes on how the script works:
    - Networks are created for each day in the directory indicated in the configuration
        file location: config["PATHS"]["STREAMING_FILES_FOLDER"]
    - This script automatically skips dates for which we already have constructed a
        retweet network

Author: John Bollenbacher, jmbollen@iu.edu (April 2, 2021)

Edited by:
- Francesco Pierri (October 11, 2021)
- Matthew DeVerna (October 14, 2021)
"""
import gzip
import json
import os

import pandas as pd

from utils import parse_cl_args, parse_config_file


def get_retweet_tuple(tweet):
    """
    Create a tuple of retweet information.

    Parameters
    ----------
    tweet (dict): A tweet object

    Returns
    -------
    tuple: (tweet_id, retweeted_tweet_id, retweeting_user_id, retweeted_user_id, time)
    """
    tweet_id = tweet["id"]
    retweeted_tweet_id = tweet["retweeted_status"]["id"]
    retweeting_user_id = tweet["user"]["id"]
    retweeted_user_id = tweet["retweeted_status"]["user"]["id"]
    time = tweet["created_at"]
    return (tweet_id, retweeted_tweet_id, retweeting_user_id, retweeted_user_id, time)


def make_retweet_networks(config):
    """
    Create retweet network for all days of data in config["PATHS"]["STREAMING_FILES_FOLDER"]
    in the form of a parquet file.

    Notes:
    ------
    - Columns: tweet_id, retweeted_tweet_id, retweeting_user_id, retweeted_user_id, time
    - Skips dates which already have a retweet network constructed.

    Parameters
    ----------
    config (dict): A dictionary with config information about paths and filenames.

    Returns
    -------
    None
    """
    # Below usually points to'/data_volume/streaming-data-UTC/'
    input_path = config["PATHS"]["STREAMING_FILES_FOLDER"]

    output_path = config["PATHS"]["RETWEET_NETWORK_FOLDER"]

    retweet_tuple_cols = [
        "tweet_id",
        "retweeted_tweet_id",
        "retweeting_user_id",
        "retweeted_user_id",
        "time",
    ]

    def get_retweet_text_tuple(tweet):
        if "extended_tweet" in tweet["retweeted_status"]:
            text = tweet["retweeted_status"]["extended_tweet"]["full_text"]
        else:
            text = tweet["retweeted_status"]["text"]
        retweeted_tweet_id = tweet["retweeted_status"]["id"]
        return (retweeted_tweet_id, text)

    retweet_text_cols = ["retweeted_tweet_id", "text"]

    # get list of files to process. exclude files already processed.
    dates = [file[-18:-8] for file in os.listdir(input_path) if ".json.gz" in file]
    skip_dates = set(
        [file[-18:-8] for file in os.listdir(output_path) if ".parquet" in file]
    )
    dates = [date for date in dates if date not in skip_dates]
    files = ["streaming_data--" + date + ".json.gz" for date in dates]

    files.sort()

    # extract data from json
    for file in files:
        print(file)
        with gzip.open(
            os.path.join(input_path, file), "rb"
        ) as zipfile:  # open raw data file
            retweets_edgelist = list()
            retweets_text = list()
            for _, line in enumerate(zipfile):
                tweet = json.loads(line)  # read one tweet object from json
                if "limit" in tweet:
                    continue  # skips rate limit error objects
                if "retweeted_status" not in tweet:
                    continue  # skip non-retweets
                retweets_text.append(get_retweet_text_tuple(tweet))
                retweets_edgelist.append(get_retweet_tuple(tweet))

        retweets_text = pd.DataFrame(retweets_text, columns=retweet_text_cols)
        retweets_text = retweets_text.drop_duplicates()
        retweets_edgelist = pd.DataFrame(retweets_edgelist, columns=retweet_tuple_cols)
        retweets_edgelist["time"] = pd.to_datetime(
            retweets_edgelist["time"], format="%a %b %d %H:%M:%S %z %Y"
        )

        retweets_edgelist.to_parquet(
            os.path.join(output_path, "retweets_edgelist_" + file[-18:-8] + ".parquet")
        )


if __name__ == "__main__":
    try:
        # Load the config file variables
        args = parse_cl_args()
        config = parse_config_file(args.config_file)

        make_retweet_networks(config)
    except Exception as e:
        print(e)
