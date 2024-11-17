# `intermediate_files/`

Intermediate files are saved here.

### Contents
- `county_2020_elections.csv`: 2020 elections data
- `data_county.npy`: aggregate SafeGraph mobility data. Contains three items ['county_matrix', 'county_idx', 'county_size']. The `county_matrix` cells represents the volume of movement between county i and county j for cell (i,j). `county_idx` is a list where each item is a FIPS county integer and the index for that county in the list is representative of the county's index in the `country_matrix` as well as the `county_size` array. `county_size` array contains the population size according to SafeGraph.
- `list_of_counties.txt`: The list of 341 counties (in FIPs code) that are included in the largest network representation that we utilize for the paper's main results.
- `LT_output.pkl`: a dictionary that contains the list of infected node IDs for each linear threshold setting.
- `url_political_alignment_score.csv`: dataframe containing political alignment scores for domains/sources.
