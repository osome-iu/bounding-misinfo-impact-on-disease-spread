"""
Purpose: 
    A script that assigns political scores to all URLs shared by all
    geolocated accounts.

Inputs:
    - Mapping from account to tweet IDs
        - Form (dict) : {account_id : [tweet_ids]}
    - Mapping from tweets to (expanded) URLs
        - Form (dict) : {tweet_id : {URL}}
    - Ideology estimation scores for domains
        - Form (pd.DataFrame) :
            - Rows = domains
            - Columns = ideology estimation scores
            - Note: est. ideology scores range from -1 to +1

Outputs:
    One .pkl file of a dictionary that has the following form...
        --> {user_id : [list of scores between -1 and +1]}
    each score represents the est. political ideology of a single domains
    shared by `user_id`

Author: Francesco Pierri & Matthew DeVerna
"""
import os
import tldextract

import pickle as pkl
import pandas as pd

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


def get_account_political(config):
    """
    Assign political scores to each URL shared by all geolocated accounts.

    Parameters:
    ----------
    - config : contents of the project configuration file

    Output:
    ----------
    A dictionary of the following form...
        --> {user_id : [list of scores between -1 and +1]}
    where each value represents the estimated ideology of the domain
    that `user_id` shared.
    """
    account_political = defaultdict(list)

    # Load account to tweet mapping
    #   Form (dict) : {user_id : [tweetid_1, tweetid_2, ..., tweetid_n]}
    #   Note: This dictionary only includes geo-located accounts
    account_tweet = pkl.load(
        open(
            os.path.join(
                config["PATHS"]["INTERMEDIATE_FILES"], config["FILES"]["ACCOUNT_TWEETS"]
            ),
            "rb",
        )
    )

    # Load tweet to URL mapping
    #   Form (dict) : {tweet_id : {URL}}
    tweet_url_mapping = pkl.load(
        open(
            os.path.join(
                config["PATHS"]["INTERMEDIATE_FILES"], config["FILES"]["TWEET_URL"]
            ),
            "rb",
        )
    )

    # Load political estimates of domains. Will create the below form
    # from the loaded .csv file
    #   Form (dict) : {website : est. political score}
    #     - est. political scores range from -1 to +1
    domain_political = pd.read_csv(
        os.path.join(
            config["PATHS"]["INTERMEDIATE_FILES"],
            config["FILES"]["URL_POLITICAL_SCORE"],
        )
    )

    # Convert dataframe to dictionary mapping domains to their ideology scores
    domain_political = {
        row["domain"]: row["score"] for ix, row in domain_political.iterrows()
    }

    """
    The below loop checks if we have an ideology score for a domain shared
    by a user and, if we do, it adds that ideology score to their list within
    the `account_political` dictionary.
    """
    for a in account_tweet:
        for tid in account_tweet[a]:
            if tid in tweet_url_mapping:
                url = tweet_url_mapping[tid]
                domain = extract_top_domain(url)
                if domain in domain_political:
                    score = domain_political[domain]
                    account_political[a].append(score)

    pkl.dump(
        account_political,
        open(
            os.path.join(
                config["PATHS"]["INTERMEDIATE_FILES"],
                config["FILES"]["ACCOUNT_POLITICAL"],
            ),
            "wb",
        ),
    )


if __name__ == "__main__":
    try:
        # Load the config file variables
        args = parse_cl_args()
        config = parse_config_file(args.config_file)

        print(
            "Getting all ideology estimates for all tweets "
            "sent by all geolocated users...."
        )
        get_account_political(config)
        exit(0)
    except Exception as e:
        print("Something's wrong!")
        print(e)
        exit(1)
