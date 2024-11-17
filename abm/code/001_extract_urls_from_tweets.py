"""
Purpose: Extract URLs from tweets. This script creates a different output file
    for every input file it reads.

Input:
    - Streaming files with tweets collected for each day (.json.gz format)

Output:
    - A dictionary, for each day, with a mapping from URL to tweet ids
        - Form (dict): {tweet_id : URL}

Authors:
    - Kaicheng Yang
    - Francesco Pierri
    - Matthew DeVerna
"""
import gzip
import json
import os
import tldextract

import glob as glob
import pickle as pkl

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


def get_urls(urls_entry):
    """
    Extract a set of URLs from a Twitter object's ["entities"]["urls"] metadata

    Parameters
    ----------
    urls_entry : Twitter's ["entities"]["urls"] object. Is a list of dictionaries
        in the following form: [{"url": "https://example.com", "expanded_url": "https://example.com"}]
        but 'expanded_url' may not be there.

    Returns
    -------
    urls (set) : A set of URLs
    """
    urls = set()
    for u in urls_entry:
        url = u["url"]
        if "expanded_url" in u:
            url = u["expanded_url"]
        urls.add(url)
    return urls


def get_dict_path(d, key_list):
    """
    Returns the values from dictionary `d` based on the list of keys indicated by `key_list`.
    If `key_list` doesn't exist, return `None`.

    Parameters
    ----------
    d (dict) : The dictionary to search
    key_list (list) : The list of keys to search in `d`. Represents the path to the value you want.

    Returns
    -------
    retval (any) : The value at the end of the path provided. If not present, returns `None`

    Example
    -------
    d = {"this": {"that": "value"}}

    get_dict_path(d, ["this", "that"]) will return "value"
    get_dict_path(d, ["this", "then"]) will return None, as the path doesn't exist
    """
    retval = d
    for k in key_list:
        if k in retval:
            retval = retval[k]
        else:
            return None
    return retval


def extract_urls(config):
    """
    Extract URLs from daily streaming files, checking both tweets/retweets and extended statuses.
    It checks whether days have been already processed to avoid repeating computations. URLs are
    further processed by the URL expander script (check "expand_urls_from_daily_dict.py") to
    account for shortened URLs.

    Parameters:
    ----------
    - config (dict): A dictionary with config information about paths and filenames.

    Output:
    ----------
    A .pkl dictionary, for each day, with the structure {'url': list(tweet_id)}
    """
    files = glob.glob(config["PATHS"]["STREAMING_FILES_FOLDER"] + "/*json.gz*")
    for file in sorted(files):  # iterating over all daily fileds
        # Example of file form: PATH/TO/STREAMING_DIR/streaming_data--YYYY-mm-dd.json.gz
        front_str = config["PATHS"]["STREAMING_FILES_FOLDER"] + "/streaming_data--"
        back_str = ".json.gz"
        day = file.replace(front_str, "").replace(back_str, "")
        print(day)

        # Skip files that have already been processed.
        out_path = os.path.join(
            config["PATHS"]["URLS_DAILY_FOLDER"], str(day) + "_urls.pkl"
        )
        if os.path.exists(out_path):
            print("Already processed!")
            continue

        urls_tweet_match = dict()
        with gzip.open(file, "r") as f:
            for line in f:
                # Check if there are URLs in any of the dictionary
                # locations listed below.
                try:
                    j = json.loads(line)
                    found_urls = set()

                    urls_entry = get_dict_path(j, ["entities", "urls"])
                    if urls_entry:
                        found_urls = found_urls.union(get_urls(urls_entry))

                    urls_entry = get_dict_path(
                        j, ["extended_tweet", "entities", "urls"]
                    )
                    if urls_entry:
                        found_urls = found_urls.union(get_urls(urls_entry))

                    urls_entry = get_dict_path(
                        j, ["retweeted_status", "entities", "urls"]
                    )
                    if urls_entry:
                        found_urls = found_urls.union(get_urls(urls_entry))

                    urls_entry = get_dict_path(
                        j, ["retweeted_status", "extended_tweet", "entities", "urls"]
                    )
                    if urls_entry:
                        found_urls = found_urls.union(get_urls(urls_entry))

                    # For each URL in the set, extract the top-level domain
                    for url in found_urls:
                        dom = extract_top_domain(url)
                        if dom == "twitter.com":  # ignore twitter.com
                            continue

                        # Add the tweet_id to that domain's key value
                        if url not in urls_tweet_match:
                            urls_tweet_match[url] = []
                        urls_tweet_match[url].append(j["id_str"])

                except Exception as e:
                    print(e)
                    print(j)
        print("Processed urls: " + str(urls_tweet_match.__len__()))
        pkl.dump(
            urls_tweet_match,
            open(out_path, "wb"),
        )


if __name__ == "__main__":
    try:
        # Load the config file variables
        args = parse_cl_args()
        config = parse_config_file(args.config_file)
        extract_urls(config)

        exit(0)
    except Exception as e:
        print(e)
        exit(1)
