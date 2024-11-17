## `environment/`

Scripts and files saved here were/can be used to generate the Python environment employed for this study.

### Environment files
As [`conda`](https://docs.conda.io/projects/conda/en/latest/index.html) can be finicky generating environments across machines, we create environment files in various ways.
- `env_mean_field.yml`: generated in the standard way but may not work with different machines
- `env_explicit_mean_field.txt`: meant to be explicit about which conda versions are utilized
- `env_from_history_mean_field.yml`: according to [condas documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#exporting-an-environment-file-across-platforms), this is meant to be the most robust YAML file to work across different types of machines.

To create the virtual environment using one of the above files, you can try one of the below calls:
- `conda env create -f env_mean_field.yml`
- `conda create --name mean_field --file env_explicit_mean_field.txt`
- `conda env create -f env_from_history_mean_field.yml`

For more information, see the [`conda` documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file).


### Scripts
We utilized [`conda`](https://docs.conda.io/projects/conda/en/latest/index.html) (V 23.3.1) to create the virtual environments that exported the above listed files.

After installing [`conda`](https://docs.conda.io/projects/conda/en/latest/index.html), we set up the environment by executing the following...
```shell
conda create -n mean_field python=3.9.12 numpy pandas matplotlib
conda activate mean_field
```

Then, we ran the below to generate the environment files in this directory.
```sh
bash create_env_yaml_files.sh
```
