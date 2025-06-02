# src/simulation_core/engine.py
import simpy
import logging
import time
from typing import List, Dict, Any
from ..agents.base_agent import BaseAgent
from .event_manager import EventManager
# from .config import SimulationConfig # Config is now a dict passed from main.py
from ..data_management.synthetic_data_generator import SyntheticDataGenerator # For default data
from ..supply_chain_network.network_model import SupplyChainNetwork
from ..supply_chain_network.nodes import Factory, Port, Warehouse, MarketNode, TransportHub # For type checking nodes
from ..agents import ( # Import specific agent types
    ExportSectorAgent,
    LogisticsAgent,
    MarketAgent,
    DisruptionAgent
)


logger = logging.getLogger(__name__)

class SimulationEngine:
    """
    Main simulation engine orchestrating the agent interactions and events.
    """
    def __init__(self, config: Dict[str, Any], supply_chain_network: SupplyChainNetwork):
        """
        Initializes the SimulationEngine.

        Args:
            config: The main simulation configuration dictionary.
            supply_chain_network: The pre-built supply chain network model.
        """
        self.config = config
        self.env = simpy.Environment()
        self.event_manager = EventManager(self.env)
        self.agents: List[BaseAgent] = []
        self.current_step = 0
        self.running = False
        self.results = {} # To store simulation outputs
        self.supply_chain_network = supply_chain_network

        sim_settings = config.get("simulation_settings", {})
        logger.info(f"SimulationEngine initialized for: {sim_settings.get('simulation_name', 'N/A')}")

    def _register_agent(self, agent: BaseAgent):
        """Registers an agent with the simulation engine."""
        self.agents.append(agent)
        logger.debug(f"Agent {agent.agent_id} registered.")

    def setup_simulation(self):
        """
        Sets up the simulation environment by creating agents based on the 
        supply_chain_network and agent configurations.
        """
        logger.info("Setting up simulation environment (agents, initial states)...")
        
        agent_configs = self.config.get("agent_configs", {})
        if not self.supply_chain_network or not self.supply_chain_network.get_all_nodes():
            logger.warning("Supply chain network is not available or has no nodes. Cannot create agents based on network nodes.")
            # Optionally, could fall back to creating some non-node-specific agents here if designed
            # For now, we rely on the network being populated.

        # Create agents based on network nodes and agent_configs
        # Example: Create ExportSectorAgents from Factory nodes
        #          Create LogisticsAgents from Port, Warehouse, TransportHub nodes
        #          Create MarketAgents from MarketNode nodes
        
        num_export_agents_to_create = agent_configs.get("num_export_sector_agents", 0)
        num_logistics_agents_to_create = agent_configs.get("num_logistics_agents", 0)
        num_market_agents_to_create = agent_configs.get("num_market_agents", 0)
        num_disruption_agents_to_create = agent_configs.get("num_disruption_agents", 0)

        created_export_agents = 0
        created_logistics_agents = 0
        created_market_agents = 0

        for node_obj in self.supply_chain_network.get_all_nodes():
            agent_config_for_node = node_obj.to_dict() # Use node's attributes as base config
            agent_config_for_node.update(self.config) # Allow global config to override/add

            if isinstance(node_obj, Factory) and created_export_agents < num_export_agents_to_create:
                agent = ExportSectorAgent(
                    agent_id=f"ExportAgent_{node_obj.node_id}",
                    simulation_engine=self,
                    config=agent_config_for_node, # Pass node-specific and global config
                    representing_node=node_obj
                )
                self._register_agent(agent)
                created_export_agents += 1
            elif isinstance(node_obj, (Port, Warehouse, TransportHub)) and created_logistics_agents < num_logistics_agents_to_create:
                agent = LogisticsAgent(
                    agent_id=f"LogisticsAgent_{node_obj.node_id}",
                    simulation_engine=self,
                    config=agent_config_for_node,
                    representing_node=node_obj
                )
                self._register_agent(agent)
                created_logistics_agents += 1
            elif isinstance(node_obj, MarketNode) and created_market_agents < num_market_agents_to_create:
                agent = MarketAgent(
                    agent_id=f"MarketAgent_{node_obj.node_id}",
                    simulation_engine=self,
                    config=agent_config_for_node,
                    representing_node=node_obj
                )
                self._register_agent(agent)
                created_market_agents += 1
        
        logger.info(f"Created {created_export_agents} ExportSectorAgents from Factory nodes.")
        logger.info(f"Created {created_logistics_agents} LogisticsAgents from Port, Warehouse, TransportHub nodes.")
        logger.info(f"Created {created_market_agents} MarketAgents from MarketNode nodes.")

        # Create DisruptionAgents (not tied to specific network nodes in this example)
        for i in range(num_disruption_agents_to_create):
            # Disruption agents might need specific config from agent_configs or a dedicated section
            disruption_agent_config = self.config.get("disruption_agent_default_config", {})
            disruption_agent_config.update(self.config) # Allow global override
            agent = DisruptionAgent(
                agent_id=f"DisruptionAgent_{i+1}",
                simulation_engine=self,
                config=disruption_agent_config
            )
            self._register_agent(agent)
        logger.info(f"Created {num_disruption_agents_to_create} DisruptionAgents.")

        if not self.agents:
            logger.warning("No agents were created during setup_simulation. The simulation might not run as expected.")
        else:
            logger.info(f"Total agents created and registered: {len(self.agents)}")

        logger.info("Simulation environment setup complete.")

    def _simulation_loop(self):
        """
        The main simulation loop process for SimPy.
        """
        sim_settings = self.config.get("simulation_settings", {})
        total_steps = sim_settings.get("total_steps", 100) # Default if not in config
        logger.info(f"Simulation starting. Duration: {total_steps} steps/days.")
        self.running = True
        start_time = time.time()

        sim_settings = self.config.get("simulation_settings", {})
        total_steps = sim_settings.get("total_steps", 100)
        for day in range(total_steps):
            self.current_step = day
            logger.info(f"--- Simulation Day: {self.current_step + 1} ---")

            # 1. Process scheduled events for the current step
            self.event_manager.process_events(self.current_step)

            # 2. Agents take their steps
            for agent in self.agents:
                try:
                    agent.step(self.current_step)
                except Exception as e:
                    logger.error(f"Error during step for agent {agent.agent_id}: {e}", exc_info=True)
            
            # 3. Collect data/metrics for this step (if any specific logic here)
            self._collect_step_metrics()

            # 4. SimPy: advance time by one day (or appropriate time unit)
            yield self.env.timeout(1) # Assuming 1 step = 1 day

            if not self.running: # Allow for early termination
                logger.info("Simulation run terminated early.")
                break
        
        self.running = False
        end_time = time.time()
        logger.info(f"Simulation finished. Total duration: {self.current_step + 1} days. Real time elapsed: {end_time - start_time:.2f} seconds.")
        self._collect_final_results()

    def run_simulation(self): # Renamed from run to match main.py call
        """
        Starts and runs the simulation.
        """
        # setup_simulation should have been called by main.py before this
        if not self.agents:
            logger.error("No agents registered. Aborting simulation. Ensure setup_simulation() was called and created agents.")
            return {}
            
        self.env.process(self._simulation_loop())
        self.env.run() # SimPy's run method
        return self.results

    def stop(self):
        """Stops the simulation if it is running."""
        if self.running:
            self.running = False
            logger.info("Stop signal received. Simulation will terminate after the current step.")

    def _collect_step_metrics(self):
        """Placeholder for collecting metrics at each simulation step."""
        # Example:
        # for agent in self.agents:
        #     if isinstance(agent, ExportSectorAgent):
        #         self.results.setdefault(f"{agent.agent_id}_inventory", []).append(agent.inventory.get("finished_goods", 0))
        pass

    def _collect_final_results(self):
        """Placeholder for collecting final results after simulation ends."""
        logger.info("Collecting final simulation results...")
        # This could summarize data collected in _collect_step_metrics or query agents for final states
        self.results["total_simulation_days"] = self.current_step + 1
        self.results["total_agents"] = len(self.agents)
        # Add more comprehensive results gathering here
        logger.info(f"Final results: {self.results}")


if __name__ == '__main__':
    # Example Usage (requires proper config and other modules)
    # Configure logging (e.g., from main.py or a utility)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logger.info("Starting example simulation engine run...")
    
    # Create a dummy config (similar to config.json structure)
    example_main_config = {
        "simulation_settings": {
            "simulation_name": "EngineTestSim",
            "total_steps": 5, # Short duration for testing
            "random_seed": 42
        },
        "logging": {"log_level": "INFO"},
        "network_config": { # Needed for synthetic data generation in main.py style
            "synthetic_params": {
                "num_factories": 1,
                "num_ports": 1,
                "num_warehouses": 1,
                "num_markets": 1, # MarketNode
                "num_transport_hubs": 0,
                "connection_probability": 1.0
            }
        },
        "agent_configs": {
            "num_export_sector_agents": 1,
            "num_logistics_agents": 2, # Port + Warehouse
            "num_market_agents": 1,
            "num_disruption_agents": 0
        }
    }
    try:
        # Simulate main.py's network creation part
        from ..utils.helpers import generate_unique_id # For node/edge creation in main style
        from ..supply_chain_network.nodes import Factory, Port, Warehouse, MarketNode # For node instantiation
        from ..supply_chain_network.edges import TransportLink # For edge instantiation

        network_gen_params = example_main_config.get("network_config", {}).get("synthetic_params", {})
        data_gen = SyntheticDataGenerator(config=network_gen_params)
        nodes_d, edges_d = data_gen.generate_network_data()
        
        scn = SupplyChainNetwork()
        node_map_example = {}
        for n_info in nodes_d:
            n_type_str = n_info.pop("type")
            n_id = n_info.get("id")
            n_info["node_id"] = n_id
            node_cls_map = {"Factory": Factory, "Port": Port, "Warehouse": Warehouse, "MarketNode": MarketNode}
            if n_type_str in node_cls_map:
                n_obj = node_cls_map[n_type_str](**n_info)
                scn.add_node(n_obj)
                node_map_example[n_id] = n_obj

        for e_info in edges_d:
            s_node = node_map_example.get(e_info["source_id"])
            t_node = node_map_example.get(e_info["target_id"])
            if s_node and t_node:
                link_p = {k:v for k,v in e_info.items() if k not in ["id", "source_id", "target_id"]}
                link_p["edge_id"] = e_info["id"]
                e_obj = TransportLink(source_node=s_node, target_node=t_node, **link_p)
                scn.add_edge(e_obj)
        logger.info(f"Example: Created SCN with {len(scn.graph.nodes)} nodes, {len(scn.graph.edges)} edges.")

        engine = SimulationEngine(config=example_main_config, supply_chain_network=scn)
        engine.setup_simulation() # Call the new setup method
        
        if not engine.agents:
             logger.warning("Engine example: No agents created by setup_simulation. Check logic.")

        results = engine.run_simulation() # Call the new run method
        logger.info(f"Example simulation finished. Results: {results}")
    except ImportError as e:
        logger.error(f"Import error during example run, likely due to relative imports: {e}")
        logger.error("This example is best run as part of the larger project structure.")
    except Exception as e:
        logger.error(f"Error during example simulation run: {e}", exc_info=True)
