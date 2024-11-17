# `sir_scripts/`

All SIR modeling simulation SLURM scripts are saved in this directory.
Each directory (e.g., `lt_1/`, `lt_2/`, etc.) contains the SLURM scripts for each linear threshold level, for each contact network (8 total).
Each contact network formulation is listed below.
For each network, we run a simulation 10 times for each linear threshold (1, 2, 4, 5, 10, and 20).

> Note: Making many separate SLURM batch scripts allows us to pass them to IU's HPC system separately, so they can run in parallel.

# Main analysis
1. 200 users minimum (per county) | proportion sampled: .1 | avg. number of edges: 25

# Robustness analysis: Sampling size
2. 200 users minimum  | proportion sampled: .01 | avg. number of edges: 25
3. 200 users minimum  | proportion sampled: .001 | avg. number of edges: 25
4. 200 users minimum  | proportion sampled: .0001 | avg. number of edges: 25

# Robustness analysis: Average number of edges
5. 200 users minimum | proportion sampled: .1 | avg. number of edges: 5
6. 200 users minimum | proportion sampled: .1 | avg. number of edges: 10
7. 200 users minimum | proportion sampled: .1 | number of edges: 15
8. 200 users minimum | proportion sampled: .1 | avg. number of edges: 20
