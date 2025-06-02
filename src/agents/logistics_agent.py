# src/agents/logistics_agent.py
from .base_agent import BaseAgent

import logging
from .base_agent import BaseAgent
from ..supply_chain_network.nodes import Port, Warehouse, TransportHub # For type hinting

logger = logging.getLogger(__name__)

class LogisticsAgent(BaseAgent):
    """
    Represents logistics network agents (e.g., Ports, Warehouses, Transport Hubs).
    """
    def __init__(self, agent_id, simulation_engine, config=None, representing_node=None):
        super().__init__(agent_id, simulation_engine, config)
        self.representing_node = representing_node
        self.node_id = None
        self.logistics_type = "GenericLogisticsNode" # Default

        if self.representing_node:
            self.node_id = self.representing_node.node_id
            # Common attributes
            self.location = self.representing_node.location
            self.operational_status = self.representing_node.operational_status

            if isinstance(self.representing_node, Port):
                self.logistics_type = "Port"
                self.processing_rate_teu_per_hour = self.representing_node.processing_rate_teu_per_hour
                self.berthing_capacity = self.representing_node.berthing_capacity
                self.storage_capacity_teu = self.representing_node.storage_capacity_teu
                self.current_congestion_level = self.representing_node.current_congestion_level
                logger.info(f"LogisticsAgent {self.agent_id} initialized for Port node {self.node_id}. Rate: {self.processing_rate_teu_per_hour} TEU/hr")
            elif isinstance(self.representing_node, Warehouse):
                self.logistics_type = "Warehouse"
                self.capacity_sqm = self.representing_node.capacity_sqm
                self.initial_inventory_units = self.representing_node.initial_inventory_units # Or map to a more detailed inventory
                self.storage_cost_per_unit_day = self.representing_node.storage_cost_per_unit_day
                self.inventory = {"general_goods": self.initial_inventory_units} # Simplified inventory
                logger.info(f"LogisticsAgent {self.agent_id} initialized for Warehouse node {self.node_id}. Capacity: {self.capacity_sqm} sqm")
            elif isinstance(self.representing_node, TransportHub):
                self.logistics_type = "TransportHub"
                self.hub_type = self.representing_node.hub_type
                self.transfer_capacity_units_per_hour = self.representing_node.transfer_capacity_units_per_hour
                self.connected_modes = self.representing_node.connected_modes
                logger.info(f"LogisticsAgent {self.agent_id} initialized for TransportHub node {self.node_id}. Type: {self.hub_type}")
            else:
                logger.warning(f"LogisticsAgent {self.agent_id} representing an unknown node type: {type(self.representing_node)}")
                self._initialize_generic_logistics_attributes()
        else:
            self._initialize_generic_logistics_attributes()
            logger.info(f"LogisticsAgent {self.agent_id} initialized (generic). Type: {self.logistics_type}")

        self.current_load = 0
        self.queue = []
        # Add more type-specific attributes based on config or node properties

    def _initialize_generic_logistics_attributes(self):
        self.logistics_type = self.config.get("logistics_type", "GenericLogistics")
        self.capacity = self.config.get("capacity", 0)
        self.location = self.config.get("location", (0,0))
        self.operational_status = self.config.get("operational_status", "OPERATIONAL")

    def step(self, current_step):
        """
        Simulates the agent's behavior for one time step.
        - Process queued items (ships, trucks, goods)
        - Manage capacity
        - Handle disruptions
        """
        # print(f"{self.agent_id} (LogisticsAgent - {self.logistics_type}) stepping at {current_step}.")
        # Placeholder logic
        self.process_queue()
        self.update_status()

    def process_queue(self):
        # Placeholder
        pass

    def update_status(self):
        # Placeholder
        pass
