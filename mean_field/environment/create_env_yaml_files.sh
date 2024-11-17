#!/bin/bash

# Create different yaml files in all the ways that conda
#   allows, since it can be finicky depending on the system.
# Our hope is that giving you all the versions make it easier to trouble shoot
#   should you run into any issues.
# 
# Note that the environment was activated prior to running this script!
# 
# Author: Matthew DeVerna

conda env export --from-history > env_from_history_mean_field.yml
conda env export > env_mean_field.yml
conda list --explicit > env_explicit_mean_field.txt

echo ""
echo "Environment files created."