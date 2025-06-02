# src/utils/helpers.py
import uuid
import yaml
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def generate_unique_id(prefix: Optional[str] = None) -> str:
    """
    Generates a unique ID string.

    Args:
        prefix: Optional prefix for the ID.

    Returns:
        A unique ID string.
    """
    uid = str(uuid.uuid4())
    if prefix:
        return f"{prefix}_{uid}"
    return uid

def load_config_yaml(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Loads a YAML configuration file.

    Args:
        file_path: Path to the YAML file.

    Returns:
        A dictionary containing the configuration, or None if an error occurs.
    """
    if not os.path.exists(file_path):
        logger.error(f"Configuration file not found: {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        logger.info(f"Successfully loaded configuration from {file_path}")
        return config_data
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file {file_path}: {e}", exc_info=True)
        return None
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}", exc_info=True)
        return None

def ensure_directory_exists(dir_path: str):
    """
    Ensures that a directory exists, creating it if necessary.
    """
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True) # exist_ok=True handles race conditions
            logger.info(f"Created directory: {dir_path}")
        except OSError as e:
            logger.error(f"Error creating directory {dir_path}: {e}")
            raise # Re-raise the exception if directory creation is critical
    else:
        if not os.path.isdir(dir_path):
            logger.error(f"Path {dir_path} exists but is not a directory.")
            raise NotADirectoryError(f"Path {dir_path} exists but is not a directory.")


if __name__ == '__main__':
    # Example usage of generate_unique_id
    id1 = generate_unique_id()
    id2 = generate_unique_id("AGENT")
    print(f"Generated ID 1: {id1}")
    print(f"Generated ID 2: {id2}")

    # Example usage of load_config_yaml
    # Create a dummy config file for testing
    dummy_config_path = "temp_config.yaml"
    dummy_data = {
        "simulation_name": "TestSim",
        "parameters": {"duration": 100, "num_agents": 10},
        "logging": {"level": "INFO"}
    }
    try:
        with open(dummy_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(dummy_data, f)
        
        loaded_conf = load_config_yaml(dummy_config_path)
        if loaded_conf:
            print(f"\nLoaded config from {dummy_config_path}:")
            print(loaded_conf)
            print(f"Simulation name: {loaded_conf.get('simulation_name')}")

        # Test non-existent file
        print("\nAttempting to load non-existent_config.yaml:")
        non_existent_conf = load_config_yaml("non_existent_config.yaml")
        if non_existent_conf is None:
            print("Correctly handled non-existent file.")

    finally:
        if os.path.exists(dummy_config_path):
            os.remove(dummy_config_path)

    # Example usage of ensure_directory_exists
    test_dir = "temp_test_dir/subdir"
    try:
        print(f"\nEnsuring directory exists: {test_dir}")
        ensure_directory_exists(test_dir)
        if os.path.isdir(test_dir):
            print(f"Directory {test_dir} successfully ensured/created.")
        # Clean up
        if os.path.exists("temp_test_dir"):
            import shutil
            shutil.rmtree("temp_test_dir")
            print(f"Cleaned up {test_dir} and its parent.")
    except Exception as e:
        print(f"Error during ensure_directory_exists test: {e}")
