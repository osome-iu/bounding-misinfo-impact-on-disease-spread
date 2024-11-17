# mean_field_quals
Code for the mean-field SIR simulations is saved here.

### Replication
We utilize Python for all simulations and figure generation.

> Note: Make sure that you visit the `environment/` directory for details on how to set up the virtual environment that we created to replicate this work.

Once the virtual environment is set up, you can run the below code from the `mean_field/` directory to delete all generated files and rerun all analyses / generate all figures.

```sh
rm -rf figures/ sim_results/ stats_results/
bash run_pipeline.sh
```

### Directories
- `environment/`: code for setting up a Python environment for the mean field scripts
- `figures/`: figures for the paper
- `figures_generation/`: scripts that generate the figures
- `sim_results/`: results of simulations run in `sim_scripts`
- `sim_scripts/`: simulation scripts
- `src/` : contains the `simulations` module, which contains all functions for running simulations
- `stats_results/`: results of `stats_scripts/print_stats.py` which prints some stats for the paper
- `stats_scripts/`: contains `print_stats.py` which prints some stats for the paper