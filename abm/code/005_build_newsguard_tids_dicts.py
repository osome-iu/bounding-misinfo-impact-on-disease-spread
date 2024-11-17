"""
Purpose: Create dictionaries that contain - for each NewsGuard
    domain - the list of tweet_ids that shared that given domain.
    See "Outputs" below for more details on what is created.

Inputs:
    - One file for each day which is a dictionary URL to tweet ids
        - Form (dict): {URL : [tweet_id]}
    - One file for each day which is a dictionary URL to its expanded form
        - Form (dict): {URL : URL_expanded}

Outputs:
    - One file for each day which is a dictionary of nested dictionaries
        in the following form:
            - keys   : NewsGuard domains
            - values : nested dictionary with the following:
                {
                    'tweet_ids' : set(tweet ids),
                    'newsguard_score' : a credibility score from 0 to 100
                }

Authors:
- Francesco Pierri
- Matthew DeVerna
"""
import os
import tldextract

import glob as glob
import pandas as pd
import pickle as pkl
from collections import defaultdict

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


def extract_newsguard_score(config):
    """
    Function to match Newsguard domains to URLs shared with tweets on a daily basis.

    Parameters:
    ----------
    - config (dict): A dictionary with config information about paths and filenames.

    Returns:
    ----------
    A dictionary of dictionaries which contains the daily set of shared tweets
    for each Newsguard domain. One file for each day. The dictionary will look like
        --> { 'domain' : { 'tweet_ids' : set(tweet_ids), 'newsguard_score' : a credibility score from 0 to 100}
    """
    ## Reading list of low- and high-credibility websites
    newsguard_df = pd.read_csv(
        os.path.join(
            config["PATHS"]["INTERMEDIATE_FILES"],
            config["FILES"]["NEWSGUARD_FILE"],
        )
    )
    newsguard_websites = set(newsguard_df["Domain"])

    # iterate over all daily urls files
    daily_urls_files = sorted(
        glob.glob(config["PATHS"]["URLS_DAILY_FOLDER"] + "/*_urls.pkl")
    )
    for file in daily_urls_files:
        # Parse the date from the filename
        day = os.path.basename(file).replace("_urls.pkl", "")
        print("Processing: " + day)

        output_path = os.path.join(
            config["PATHS"]["URLS_DAILY_FOLDER"], day + "_newsguard_match.pkl"
        )
        if os.path.exists(output_path):
            print("Already processed!")
            continue

        # Load daily URL to tweet id mapping
        #   Form (dict): {URL : [tweet_id]}
        urls_tweet_match = pkl.load(open(file, "rb"))

        # Load URL to expanded URL mapping (both strings)
        #   Form (dict): {URL : URL_expanded}
        urls_expanded_dict = pkl.load(
            open(file.replace("_urls.pkl", "_urls_expanded.pkl"), "rb")
        )

        domain_tids = defaultdict(list)

        # Iterate through all urls for a given day
        for u in urls_tweet_match:
            # Grab all tweet ids that sent that url
            tids = urls_tweet_match[u]

            # If that urls is in the `expanded_dict` then
            # we have an expanded version of that URL, so we take
            # that one
            if u in urls_expanded_dict:
                full_url = urls_expanded_dict[u]
            else:
                full_url = u

            # Extract the top level domain and add the tweet_ids that
            # were shared for that domain on this day but only if it
            # is within the New Guard data set
            domain = extract_top_domain(full_url)
            if domain in newsguard_websites:
                domain_tids[domain] += tids

        # Build the final output dictionary and save the .pkl file
        ng_match = dict()
        for domain in domain_tids:
            tids = set(domain_tids[domain])
            ng_score = newsguard_df[newsguard_df["Domain"] == domain]["Score"].values[0]
            ng_match[domain] = {"tids": tids, "ng_score": ng_score}

        pkl.dump(ng_match, open(output_path, "wb"))


if __name__ == "__main__":
    try:
        # Load the config file variables
        args = parse_cl_args()
        config = parse_config_file(args.config_file)
        extract_newsguard_score(config)

        exit(0)
    except Exception as e:
        print(e)
        exit(1)
