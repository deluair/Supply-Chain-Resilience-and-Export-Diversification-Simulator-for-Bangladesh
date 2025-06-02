# main.py
import json
import logging
import os
import sys

# Ensure the src directory is in the Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from utils.logger_config import setup_logging, get_project_logger, DEFAULT_LOG_LEVEL
from utils.helpers import load_config_yaml, generate_unique_id, ensure_directory_exists
from data_management.synthetic_data_generator import SyntheticDataGenerator
from supply_chain_network.network_model import SupplyChainNetwork
from simulation_core.engine import SimulationEngine
# Import node and edge types for synthetic data generation
from supply_chain_network.nodes import FactoryNode, PortNode, WarehouseNode, MarketNode, TransportHubNode
from supply_chain_network.edges import TransportLink


CONFIG_FILE_PATH = os.path.join(PROJECT_ROOT, "config", "config.json")

def main():
    """
    Main function to initialize and run the Bangladesh Supply Chain Simulator.
    """
    # 1. Load Configuration
    config = load_config_yaml(CONFIG_FILE_PATH)
    if not config:
        # Fallback basic logging if config fails, so this message is seen
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error(f"Critical Error: Could not load configuration from {CONFIG_FILE_PATH}. Exiting.")
        sys.exit(1)

    # 2. Setup Logging
    log_config = config.get("logging", {})
    log_level_str = log_config.get("log_level", "INFO").upper()
    console_log_level_str = log_config.get("console_log_level", log_level_str).upper()
    
    log_level = getattr(logging, log_level_str, DEFAULT_LOG_LEVEL)
    console_log_level = getattr(logging, console_log_level_str, log_level)

    log_file_relative = log_config.get("log_file", "logs/simulation.log")
    log_file_absolute = os.path.join(PROJECT_ROOT, log_file_relative)
    log_dir = os.path.dirname(log_file_absolute)
    
    try:
        ensure_directory_exists(log_dir)
    except Exception as e:
        # Fallback basic logging if directory creation fails
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error(f"Critical Error: Could not create log directory {log_dir}: {e}. Exiting.", exc_info=True)
        sys.exit(1)

    setup_logging(
        log_level=log_level,
        log_file=log_file_absolute,
        console_log_level=console_log_level,
        max_bytes=log_config.get("max_log_file_bytes", 10*1024*1024),
        backup_count=log_config.get("log_backup_count", 5)
    )
    
    logger = get_project_logger(__name__)
    logger.info("--- Starting Bangladesh Supply Chain Simulator ---")
    logger.info(f"Configuration loaded successfully from {CONFIG_FILE_PATH}")
    sim_settings = config.get("simulation_settings", {})
    logger.info(f"Simulation Name: {sim_settings.get('simulation_name', 'N/A')}")
    logger.info(f"Total Steps: {sim_settings.get('total_steps', 'N/A')}")

    # 3. Initialize Core Components
    network_config = config.get("network_config", {})
    
    # Pass the synthetic_params dict from network_config to the generator
    data_generator = SyntheticDataGenerator(config=network_config.get("synthetic_params", {}))
    supply_chain_network = SupplyChainNetwork()

    # 4. Build Supply Chain Network
    logger.info("Building supply chain network...")
    if network_config.get("data_source_type") == "synthetic":
        logger.info("Using synthetic data to build the network.")
        
        # This method will need to be implemented in SyntheticDataGenerator
        nodes_data, edges_data = data_generator.generate_network_data() 
        
        node_map = {} # To map generated IDs to node objects for edge creation
        for node_info in nodes_data:
            node_type_str = node_info.pop("type", "Unknown") # e.g., "Factory", "Port"
            node_id = node_info.get("id", generate_unique_id(node_type_str.lower()))
            node_info["node_id"] = node_id # Ensure id is in dict for constructor
            
            node_class_map = {
                "Factory": FactoryNode, "Port": PortNode, "Warehouse": WarehouseNode,
                "MarketNode": MarketNode, "TransportHub": TransportHubNode # Corrected key to "MarketNode"
            }
            node_class = node_class_map.get(node_type_str)
            
            if node_class:
                try:
                    node_obj = node_class(**node_info)
                    supply_chain_network.add_node(node_obj)
                    node_map[node_id] = node_obj
                except Exception as e:
                    logger.error(f"Error instantiating node {node_id} of type {node_type_str}: {e}", exc_info=True)
            else:
                logger.warning(f"Unknown node type '{node_type_str}' for id '{node_id}' in synthetic data. Skipping.")
        logger.info(f"Added {len(supply_chain_network.get_all_nodes())} nodes from synthetic data.")

        for edge_info in edges_data:
            edge_id = edge_info.get("id", generate_unique_id("link"))
            source_id = edge_info.get("source_id")
            target_id = edge_info.get("target_id")
            
            source_node = node_map.get(source_id)
            target_node = node_map.get(target_id)

            if source_node and target_node:
                try:
                    # Prepare edge_info for TransportLink constructor
                    link_params = {k: v for k, v in edge_info.items() if k not in ["id", "source_id", "target_id"]}
                    link_params["edge_id"] = edge_id 
                    
                    edge_obj = TransportLink(
                        source_node=source_node,
                        target_node=target_node,
                        **link_params
                    )
                    supply_chain_network.add_edge(edge_obj)
                except Exception as e:
                    logger.error(f"Error instantiating edge {edge_id} between {source_id} and {target_id}: {e}", exc_info=True)
            else:
                logger.warning(f"Could not create edge {edge_id}: source '{source_id}' or target '{target_id}' node not found or failed to instantiate.")
        logger.info(f"Added {len(supply_chain_network.get_all_edges())} edges from synthetic data.")
        
        if network_config.get("visualize_on_startup", False):
            viz_path = os.path.join(PROJECT_ROOT, "logs", f"{sim_settings.get('simulation_name', 'network')}_synthetic.png")
            supply_chain_network.visualize_network(save_path=viz_path)
            logger.info(f"Synthetic network visualization saved to {viz_path}")

    elif network_config.get("data_source_type") == "file":
        file_path = network_config.get("network_data_file", "data/processed/network_definition.json")
        abs_file_path = os.path.join(PROJECT_ROOT, file_path)
        logger.info(f"Attempting to build network from file: {abs_file_path}")
        # This method already exists in SupplyChainNetwork
        success = supply_chain_network.build_from_config_file(abs_file_path) 
        if not success:
            logger.error(f"Failed to build network from file {abs_file_path}. Check logs for details. Exiting.")
            sys.exit(1)
    else:
        logger.error(f"Unknown network_config.data_source_type: {network_config.get('data_source_type')}. Exiting.")
        sys.exit(1)
    
    if not supply_chain_network.get_all_nodes():
        logger.warning("The supply chain network is empty. Simulation might not produce meaningful results.")
    else:
        logger.info(f"Supply chain network built successfully with {len(supply_chain_network.graph.nodes)} nodes and {len(supply_chain_network.graph.edges)} edges.")


    # 5. Initialize Simulation Engine
    logger.info("Initializing Simulation Engine...")
    sim_engine = SimulationEngine(
        config=config, 
        supply_chain_network=supply_chain_network
    )
    logger.info("Simulation Engine initialized.")

    # 6. Setup Simulation Environment (includes agent creation)
    logger.info("Setting up simulation environment...")
    sim_engine.setup_simulation() # This will create agents based on config
    logger.info("Simulation environment setup complete.")

    # 7. Run Simulation
    logger.info(f"Starting simulation run for {sim_settings.get('total_steps')} steps...")
    sim_engine.run_simulation()
    logger.info("Simulation run finished.")

    # 8. (Future) Analyze Results and Generate Reports
    # logger.info("Analyzing results and generating reports (placeholder)...")
    # results = sim_engine.get_results() # Requires get_results() in SimulationEngine
    # report_generator = ReportGenerator(config, results) # Requires ReportGenerator
    # report_generator.generate_summary_report()
    # logger.info("Reports generated.")

    logger.info("--- Bangladesh Supply Chain Simulator execution finished ---")
    print("Bangladesh Supply Chain Simulator - Execution Finished. Check logs for details.")

if __name__ == "__main__":
    main()
