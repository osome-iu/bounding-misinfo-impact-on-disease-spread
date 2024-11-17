"""
Purpose: Expand shortened URLs. This script creates a different output file
    for every input file it reads.

Input:
    - Mapping from URL to a list of tweet ids (which contained that URL), for each day
        - Form (dict): {URL : [tweet_id]}

Output:
    - Mapping from URL to expanded URL, for each day
        - Form (dict): {URL : URL_expanded}
        - Short URLs only

Authors:
    - Kaicheng Yang
    - Francesco Pierri
    - Matthew DeVerna
"""
import concurrent.futures
import glob
import os
import urlexpander
import queue
import requests
import tldextract

import pandas as pd
import pickle as pkl
from urllib.parse import urlparse

from utils import parse_cl_args, parse_config_file

HEADERS = {
    "user-agent": "Mozilla/5.0 (compatible; HoaxyBot/1.0 +http://cnets.indiana.edu; truthy@indiana.edu)"
}
HTTP_TIMEOUT = 20


def fetch_full_url(short_url):
    """
    Fetch the full URL of a short_url by sending an HTTP HEAD request.

    Parameters:
    ----------
    short_url (str): Shortened URL to fetch the full URL of

    Returns:
    -------
    str: Full URL of the shortened URL
    """
    try:
        r = requests.head(
            short_url, allow_redirects=True, headers=HEADERS, timeout=HTTP_TIMEOUT
        )
        base_url = r.url
        if not base_url.endswith("/"):
            base_url = base_url + "/"
    except Exception as e:
        print(e)
        base_url = short_url
    return base_url


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


def expand_urls(config):
    """
    Expand all shortened URLs in various input files.
    """
    print("Begin extracting urls...")

    short_link_services = [
        "bit.ly",
        "dlvr.it",
        "liicr.nl",
        "tinyurl.com",
        "goo.gl",
        "ift.tt",
        "ow.ly",
        "fxn.ws",
        "buff.ly",
        "back.ly",
        "amzn.to",
        "nyti.ms",
        "nyp.st",
        "dailysign.al",
        "j.mp",
        "wapo.st",
        "reut.rs",
        "drudge.tw",
        "shar.es",
        "sumo.ly",
        "rebrand.ly",
        "covfefe.bz",
        "trib.al",
        "yhoo.it",
        "t.co",
        "shr.lc",
        "po.st",
        "dld.bz",
        "bitly.com",
        "crfrm.us",
        "flip.it",
        "mf.tt",
        "wp.me",
        "voat.co",
        "zurl.co",
        "fw.to",
        "mol.im",
        "read.bi",
        "disq.us",
        "tmsnrt.rs",
        "usat.ly",
        "aje.io",
        "sc.mp",
        "gop.cm",
        "crwd.fr",
        "zpr.io",
        "scq.io",
        "trib.in",
        "owl.li",
        "youtu.be",
    ]

    for file in sorted(glob.glob(config["PATHS"]["URLS_DAILY_FOLDER"] + "/*_urls.pkl")):
        # Extract the date from the file name
        day = os.path.basename(file).replace("_urls.pkl", "")
        print(day)

        # Skip the files that have already been processed.
        output_path = os.path.join(
            config["PATHS"]["URLS_DAILY_FOLDER"], str(day) + "_urls_expanded.pkl"
        )
        if os.path.exists(output_path):
            print("Already expanded!")
            continue

        # Otherwise, we must expand URLs
        else:
            url_file = os.path.join(
                config["PATHS"]["URLS_DAILY_FOLDER"], str(day) + "_urls.pkl"
            )
            urls_dict = pkl.load(open(url_file, "rb"))

        # Check if the url is a short url and save for later expansion.
        urls_to_expand = []
        for url in urls_dict:
            domain = urlparse(url).netloc
            if domain in short_link_services:
                urls_to_expand.append(url)

        print("No. urls to expand: " + str(urls_to_expand.__len__()))

        # Do main expansion
        q = queue.Queue()

        def expand_domain(short_url):
            expanded_url = fetch_full_url(short_url)
            top_domain = extract_top_domain(expanded_url)
            q.put([short_url, expanded_url, top_domain])

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(expand_domain, urls_to_expand)

        df = pd.DataFrame(
            list(q.queue), columns=["short_url", "expanded_url", "top_domain"]
        )

        # Check if the expanded url is the same as the original and, if so, use the
        # urlexpander package to try and further expand it
        print("Updating links")
        expanded_urls_dict = dict()
        for ix, row in df.iterrows():
            old = row["short_url"]
            new = row["expanded_url"]
            if old == new:
                try:
                    # try to further expand it with urlexpander
                    new = urlexpander.expand(old)
                except:
                    continue
            expanded_urls_dict[old] = new
            pkl.dump(expanded_urls_dict, open(output_path, "wb"))


if __name__ == "__main__":
    try:
        # Load the config file variables
        args = parse_cl_args()
        config = parse_config_file(args.config_file)

        print("Expanding URLs.")
        expand_urls(config)
        exit(0)
    except:
        print("Something's wrong.")
        exit(1)
