"""
Purpose: Simulate a modified SIR model on a network.

Input:
    - Contact network
    - Table of account information

Output:
    - Results of SIR simulations

Authors:
    - Francesco Pierri
    - Matthew DeVerna
"""
import argparse
import configparser
import datetime
import os
import random
import sys
import traceback

import igraph as ig
import pandas as pd
import pickle as pkl

# UPDATE FOR YOUR OWN SYSTEM
CONFIG_FILE_PATH = (
    "/N/slate/mdeverna/bounding-misinfo-impact-on-disease-spread/abm/code/config.ini"
)

NUM_EXPERIMENTS = 10
EPI_STEPS = 100


class SIRmodel:
    """
    A class to simulate a SIR model on a network.
    """

    def __init__(
        self,
        graph,
        beta_min=0.01,
        beta_max=1.0,
        recovery_time=5,
        outbreak_size=10,
    ):
        """
        Initialize the class with the network and epidemiological parameters.

        Parameters
        ----------
        - graph (igraph.Graph) : The contact network
        - beta_min (float) : The minimum value of beta (referred to as "p" in the paper)
            - This is the value for ordinary individuals
        - beta_max (float) : The maximum value of beta (referred to as "p" in the paper)
            - This is the value for misinformed individuals
        - recovery_time (int) : The number of days it takes for an individual to recover
        - outbreak_size (int) : The number of individuals in the initial infected set
        """
        self.graph = graph
        self.beta_max = beta_max
        self.beta_min = beta_min
        self.recovery_time = recovery_time
        self.gamma = 1 / recovery_time
        self.outbreak_size = outbreak_size

    def initialize_nodes(self):
        """
        Initialize nodes to susceptible compartment and set misinformation
        equal to the specified variable
        """
        # This is specific to each node.
        self.graph.vs["misinfo"] = [node["opinion"] for node in self.graph.vs]
        # These are the same for everyone at initialization time
        self.graph.vs["status"] = ["S" for _ in range(self.graph.vcount())]
        self.graph.vs["infector"] = ["" for _ in range(self.graph.vcount())]
        self.graph.vs["infection_time"] = [-1 for _ in range(self.graph.vcount())]
        self.graph.vs["recovery_time"] = [-1 for _ in range(self.graph.vcount())]

    def random_outbreak(self):
        """
        Randomly infect an `OUTBREAK_SIZE` number of nodes
        """
        nodes = list(self.graph.vs)
        random.shuffle(nodes)
        for node in nodes[: self.outbreak_size]:
            node["status"] = "I"
            node["infection_time"] = 0

    def compute_individual_beta(self, node):
        """
        Calculate the beta value of the provided individual `node`.
        Referred to as 'p' in the paper.
        """
        return self.beta_min + (self.beta_max - self.beta_min) * node["misinfo"]

    def simulate_nodal_infection(self, node, step):
        """
        Simulate potential infection for `node` at timestep `step` by iterating
        over all neighbors
        """
        beta_node = self.compute_individual_beta(node)

        # For all neighbors of `node`, check if they are infected and
        # flip a coin to potentially infect `node` based on it's beta value
        for neighbor in node.neighbors():
            if neighbor["status"] == "I":
                random_number = random.random()
                if random_number < beta_node:
                    node["status"] = "I"
                    node["infection_time"] = step
                    node["infector"] = neighbor["userID"]
                    break

    def simulate_infection_step(self, step):
        """
        Simulate a timestep in the entire network iterating over all nodes randomly
        """
        nodes = list(self.graph.vs)
        random.shuffle(nodes)
        for node in nodes:
            node_status = node["status"]

            # If node is susceptible, simulate potential infection
            if node_status == "S":
                self.simulate_nodal_infection(node, step)
                continue

            # If infected, simulate potential recovery
            if node_status == "I":
                if random.random() < self.gamma:
                    node["status"] = "R"
                    node["recovery_time"] = step


# -------------- Separate functions --------------
# ------------------------------------------------
def parse_arguments():
    """
    Parses command line arguments for linear threshold and contact network file.

    Returns:
        argparse.Namespace: Parsed arguments with lt_threshold and cnet_file.
    """
    # Define the possible values for the linear threshold as a constant
    POSSIBLE_LT_VALUES = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        20,
        30,
        40,
        50,
        60,
        75,
        100,
    ]

    # Create the parser
    parser = argparse.ArgumentParser(description="Run SIR simulations.")

    # Add arguments
    parser.add_argument(
        "--lt_threshold",
        "-lt",
        type=int,
        choices=POSSIBLE_LT_VALUES,
        help="Linear threshold value.",
        required=True,
    )
    parser.add_argument(
        "--cnet_file",
        "-c",
        type=str,
        help="Full path to the contact network file.",
        required=True,
    )

    # Parse arguments
    args = parser.parse_args()

    return args


def extract_parameters(file):
    """
    Return a dictionary of parameters that were used to create a contact
    network, based on the file name.
    """
    parameters = {}

    # Define the parameter names
    parameters_set = {"minusers", "numedges", "propsampled"}

    # Split the file name into sections
    file_sections = file.split("__")

    # Iterate through each section to find and extract parameters
    for section in file_sections[1:]:
        for param in parameters_set:
            if param in section:
                _, value = section.split(param + "_")

                # Handles the end of the file name
                if "." in value:
                    # Extract the value before the file extension
                    value = value.rsplit(".", 1)[0]

                parameters[param] = value
    return parameters


def create_output_file_name(
    lt_threshold,
    pop_sampled,
    min_user_thresh,
    num_edges,
):
    """
    Create an output file name that captures the important information about the SIR simulation.
    """
    try:
        now = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d_%H-%M")
        output_name = (
            f"{now}__SIR_results__"
            f"lt_threshold_{lt_threshold}__"
            f"pop_sampled_{pop_sampled}__"
            f"min_user_thresh_{min_user_thresh}__"
            f"num_edges_{num_edges}.parquet"
        )

    except Exception as e:
        print(e)
        raise Exception("Problem creating output file name!")
    return output_name


def check_file_exists(
    lt_threshold, min_user_threshold, num_edges_to_draw, sample_prop, output_dir
):
    """
    Check if a file with the specified parameters already exists in the output directory.
    Ignores the datetime part of the file name.
    """
    try:
        # Construct the parameter part of the file name
        param_part = (
            f"lt_threshold_{lt_threshold}__"
            f"pop_sampled_{sample_prop}__"
            f"min_user_thresh_{min_user_threshold}__"
            f"num_edges_{num_edges_to_draw}.parquet"
        )

        for file in os.listdir(output_dir):
            if file.endswith(param_part):
                return True

        return False

    except Exception as e:
        print(e)
        raise Exception("Problem checking if file exists!")


def run_SIR_experiments(config):
    """
    Run a number of SIRH simulations over a contact network that incorporates
        levels of misinformation based on the model described above.
    Function Parameters:
    ----------
    - config (configparser.ConfigParser) : a configuration file
        that contains all variables/paths/files for this project.
    """
    print("Exctracting necessary paths from config...")
    output_dir = config["PATHS"]["SIMULATION_RESULTS"]
    os.makedirs(output_dir, exist_ok=True)
    intermediate_dir = config["PATHS"]["INTERMEDIATE_FILES"]
    lt_data = config["FILES"]["LT_OUTPUT"]

    print("Loading epidemiological parameters from command line...")
    # Get script inputs
    args = parse_arguments()
    lt_threshold = args.lt_threshold
    cnet_file = args.cnet_file
    if not os.path.isabs(cnet_file):
        raise Exception(
            "Contact network file must be an absolute path."
            f"Provided path is: {cnet_file}"
        )

    # Extract parameters from the cnet file basename
    parameters = extract_parameters(os.path.basename(cnet_file))
    pop_sampled = float(parameters["propsampled"])
    min_user_thresh = int(parameters["minusers"])
    num_edges = int(parameters["numedges"])

    # Create output file name and full path
    output_file_name = create_output_file_name(
        lt_threshold,
        pop_sampled,
        min_user_thresh,
        num_edges,
    )
    file_exists = check_file_exists(
        lt_threshold, min_user_thresh, num_edges, pop_sampled, output_dir
    )
    if file_exists:
        print(f"File already exists!")
        print(f"Filename: {output_file_name}")
        print(f"Location: {output_dir}")
        sys.exit(0)
    os.makedirs(output_dir, exist_ok=True)
    out_fname = os.path.join(output_dir, output_file_name)

    # Load in necessary files based on input
    print("Reading contact network...")
    g = ig.load(cnet_file, format="gml")
    graph = g.copy()

    print("Reading LT model output to label nodes as misinformed...")

    # Build LT threshold file path
    lt_full_path = os.path.join(intermediate_dir, lt_data)

    # Load the data. Dictionary where...
    #   key: LT threshold
    #   value: set of misinformed users
    LT_output = pkl.load(open(lt_full_path, "rb"))

    # Set whether nodes are misinformed or not -> Default is 0 == not misinformed.
    graph.vs["opinion"] = [0 for _ in range(graph.vcount())]
    no_misinfo_nodes = 0
    for node in graph.vs:
        # This dictionary contains the set of misinformed users after marking
        # nodes as misinformed or not
        if node["userID"] in LT_output[lt_threshold]:
            node["opinion"] = 1
            no_misinfo_nodes += 1
    print(
        "Number of misinformed nodes: "
        f"{no_misinfo_nodes:,} out of {graph.vcount():,}"
    )

    # Remove isolated nodes (just incase)
    zero_degree_nodes = [
        node for node in graph.vs if graph.vs.find(node["name"]).degree() == 0
    ]
    graph.delete_vertices(zero_degree_nodes)

    print("Initializing SIR model.")
    SIR = SIRmodel(graph=graph)

    print("Begin simulations with below parameters:")
    print("---------------------------------------")
    print(f"\t- Linear threshold      : {lt_threshold}")
    print(f"\t- Contact network edges : {num_edges}")
    print(f"\t- Prop. of pop. sampled : {pop_sampled}")
    print(f"\t- Min. user per county  : {min_user_thresh}")
    print("---------------------------------------")

    exp_results = []
    for n_exp in range(1, NUM_EXPERIMENTS + 1):
        print(f"Initializing experiment: {str(n_exp)}")

        # NOTE: SIR.initialize_nodes() resets all nodes compartments and all simulation
        # results. So we do not need to recreate the SIR class each time.
        SIR.initialize_nodes()
        SIR.random_outbreak()

        print("Starting now.")
        print("Step :", end=" ")
        for t in range(1, EPI_STEPS + 1):
            if t == 100:
                print(t, end="\n")
            else:
                print(t, end=", ")

            SIR.simulate_infection_step(t)

        # Add the experiment number here. This is overwritten each time
        # for all nodes. They are then added to the list as new items.
        for node in SIR.graph.vs:
            node.update_attributes({"exp": n_exp})
            exp_results.append(node.attributes())

    # Save results as parquet. File name includes all parameters used in the simulation
    exp_results_df = pd.DataFrame(exp_results, index=range(len(exp_results)))
    exp_results_df.to_parquet(out_fname)


if __name__ == "__main__":
    try:
        if not os.path.exists(CONFIG_FILE_PATH):
            raise Exception(
                f"Config file not found!\n Expected file: {CONFIG_FILE_PATH}"
            )

        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)

        print("Running SIR simulation.")
        run_SIR_experiments(config)
        print("~~~ Script complete! ~~~")

    except Exception as e:
        print(e)
        traceback.print_exc()
        print("Something's wrong.")
