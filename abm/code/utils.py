"""
Convenience functions used in scripts throughout the project.
"""
import argparse
import configparser


def parse_cl_args():
    """Set CLI Arguments."""
    print("Attempting to parse command line arguments...")

    try:
        # Initialize parser
        parser = argparse.ArgumentParser()
        # Add optional arguments
        parser.add_argument(
            "-c",
            "--config-file",
            metavar="Config-file",
            help="Full path to the project's "
            "config.ini file containing paths/file names for script.",
            required=True,
        )

        # Read parsed arguments from the command line into "args"
        args = parser.parse_args()
        print("Success.")
        # Assign the config file name to a variable and return it
        return args

    except Exception as e:
        print("Problem parsing command line input.")
        print(e)


def parse_config_file(config_file_path):
    """Parse config file from provided path"""

    try:
        config = configparser.ConfigParser()
        config.read(config_file_path)
        return config

    except Exception as e:
        print("Problem parsing config file.")
        print(e)
