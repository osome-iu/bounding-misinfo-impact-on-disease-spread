## `code/`

Code for the agent-based modeling portion of the project is saved here.

### Contents

#### Scripts

> Note: bash/SLURM files which share prefix numbers with Python scripts are utilized to run the associated Python script with IU's high performance computing system. This is _necessary_ given the size of the networks. E.g., multiple simulations on networks that are larger than 20GBs themselves, requires > 100GBs of RAM.

- `001_extract_urls_from_tweets.py`: Extract URLs from tweets. This script creates a different output file for every input file it reads.
- `002_make_retweets_network.py`: Create retweet networks from CoVaxxy streaming data.
- `003_account_tid_location_match.py`: Extract locations from accounts for each day of Twitter data,  and it maps each user to its location and the set of tweet ids shared on each day. It also combines all location in a unique mapping from user to location.
- `004_expand_urls.py`: Expand shortened URLs. This script creates a different output file for every input file it reads.
- `005_build_newsguard_tids_dicts.py`: Create dictionaries that contain - for each NewsGuard domain - the list of tweet_ids that shared that given domain.
- `006_map_tweets_to_cred_score.py`: Mapping tweets, users, URLs and credibility score according to Newsguard.
- `007_build_global_rt_network.py`: Create a global directed weighted retweeting network for users geolocated in US counties.
- `008_get_political_score.py`: A script that assigns political scores to all URLs shared by all geolocated accounts.
- `009_build_account_table.py`: Create an account table that includes location, estimated ideology score, and percentage of misinformation shared by individual user.
- `010_propagate_political.py`: Propagate the political scores of users within our Twitter network to their neighbors. We assume some degree of homophily, so that we can (for users without their own estimated political ideology) take the average estimated ideology of all their neighbors.
- `011_build_contact_network.py`: Create a contact network by taking a stratified sample of the Twitter network.
- `011_build_contact_networks_all.sh`: Build all contact networks with SLURM in parallel by running the scripts in the `build_scripts/` directory.
- `012_build_global_network_with_node_attributes.py`: Create a weighted directed retweeting graph in .gexf format with node-level attributes.
- `013_linear_threshold_misinformed_spread.py`: Run one step of the linear threshold opinion spreading dynamics on a retweeting graph of geolocated Twitter users within the United States.
- `013_lt_misinformed_spreading_all.script`: Run the above script.
- `014_sir_modeling.py`: Simulate a SMIR model on a network.
- `014_sir_simulations_all.sh`: Submit SLURM batch scripts located in subdirectories of sir_scripts.
- `015_clean_experiments.py`: A script to ingest and clean all experimental results. 
- `015_clean.script`: Run the above script.
- `016_paper_stats.py`: Calculate numbers presented within the abm analysis of the paper.
- `017_generate_list_of_counties.py`: Create the list of county FIP codes that were utilized in the largest network.
- `018_generate_figures.sh`: Generate all figures by running the `plotting_scripts/` scripts.

#### Directories
- `build_scripts/`: SLURM scripts to generate different contact networks
- `sir_scripts/`: SLURM scripts to run all simulation configurations
- `plotting_scripts/`: scripts to generate figures

#### Miscellaneous
- `config.ini` : configuration file utilized throughout the project for various paths/files. You'll need to update this for your own environment.
- `utils.py`: module with a couple of convenience functions

### Replication notes and data
The final, aggregate simulation data can be found in the `/data/simulations_clean/` directory and can be utilized to generate the figures in our paper with the `018_generate_figures.sh` script.

A good portion of this code (scripts 001-007) require raw streaming data, and others utilized NewsGuard data, which we cannot share for contractual reasons.
Furthermore, all of the data files utilized in this repository total ~344 GBs.
Files we are allowed to share and whose size does not exceed GitHub's single file limits, are available.
For other data, please reach out to the [Observatory on Social Media](https://osome.iu.edu/).
Currently, a contact page can be found here: https://osome.iu.edu/about/contact

See the `./abm/requirements.txt` file for environment details.

#### CoVaxxy Data
If you would like to access the tweet IDs collected as part of the [CoVaxxy dataset](https://doi.org/10.1609/icwsm.v15i1.18122), please see these resources:
- Tweet IDs can be found here for rehydration: https://zenodo.org/records/7752586
- See the CoVaxxy dataset paper here: https://doi.org/10.1609/icwsm.v15i1.18122
- See the CoVaxxy data dashboard: https://osome.iu.edu/tools/covaxxy
