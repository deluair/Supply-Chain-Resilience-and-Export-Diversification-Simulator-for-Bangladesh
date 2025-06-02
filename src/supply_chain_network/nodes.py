# src/supply_chain_network/nodes.py
import uuid
from typing import Optional, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class BaseNode:
    """
    Represents a generic node in the supply chain network graph.
    This is a data-centric representation, distinct from an 'Agent',
    though an Agent may operate at or represent a Node.
    """
    def __init__(self, node_id: str, name: str, node_type: str,
                 location: Optional[Tuple[float, float]] = None, # (lat, lon)
                 capacity: Optional[float] = None,
                 attributes: Optional[Dict[str, Any]] = None):
        self.id: str = node_id # Expect node_id to be provided, or handle upstream if None is allowed
        if not self.id:
            self.id = str(uuid.uuid4())
            logger.warning(f"Node '{name}' of type '{node_type}' was created without a node_id. Generated UUID: {self.id}")
        self.name: str = name
        self.type: str = node_type # e.g., "Port", "Factory", "Market", "Warehouse", "ICD"
        self.location: Optional[Tuple[float, float]] = location
        self.capacity: Optional[float] = capacity # Generic capacity, units depend on node type
        self.attributes: Dict[str, Any] = attributes if attributes else {}
        # Link to an agent instance if this node is directly managed by one
        self.agent_id: Optional[str] = None

        logger.debug(f"Node created: {self.id} ({self.name}, type: {self.type})")

    def __repr__(self):
        return f"<Node(id={self.id}, name='{self.name}', type='{self.type}')>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "capacity": self.capacity,
            "attributes": self.attributes,
            "agent_id": self.agent_id,
        }

class FactoryNode(BaseNode):
    def __init__(self, node_id: str, name: str, 
                 factory_type: str = "GenericFactory", 
                 production_capacity_units_per_day: float = 0.0,
                 raw_material_requirements: Optional[Dict[str, float]] = None,
                 initial_inventory_units: float = 0.0,
                 operational_status: str = "OPERATIONAL",
                 **kwargs):
        super().__init__(node_id, name, node_type="Factory", **kwargs)
        self.factory_type = factory_type
        self.production_capacity_units_per_day = production_capacity_units_per_day
        self.raw_material_requirements = raw_material_requirements if raw_material_requirements else {}
        self.initial_inventory_units = initial_inventory_units
        self.operational_status = operational_status # Also store in attributes if BaseNode handles it
        self.attributes.update({
            'factory_type': self.factory_type,
            'production_capacity_units_per_day': self.production_capacity_units_per_day,
            'raw_material_requirements': self.raw_material_requirements,
            'initial_inventory_units': self.initial_inventory_units,
            'operational_status': self.operational_status
        })

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "factory_type": self.factory_type,
            "production_capacity_units_per_day": self.production_capacity_units_per_day,
            "raw_material_requirements": self.raw_material_requirements,
            "initial_inventory_units": self.initial_inventory_units,
            "operational_status": self.operational_status
        })
        return data

class PortNode(BaseNode):
    def __init__(self, node_id: str, name: str, 
                 processing_rate_teu_per_hour: float = 0.0,
                 berthing_capacity: int = 0,
                 storage_capacity_teu: float = 0.0,
                 current_congestion_level: float = 0.0,
                 operational_status: str = "OPERATIONAL",
                 **kwargs):
        super().__init__(node_id, name, node_type="Port", **kwargs)
        self.processing_rate_teu_per_hour = processing_rate_teu_per_hour
        self.berthing_capacity = berthing_capacity
        self.storage_capacity_teu = storage_capacity_teu
        self.current_congestion_level = current_congestion_level
        self.operational_status = operational_status
        self.attributes.update({
            'processing_rate_teu_per_hour': self.processing_rate_teu_per_hour,
            'berthing_capacity': self.berthing_capacity,
            'storage_capacity_teu': self.storage_capacity_teu,
            'current_congestion_level': self.current_congestion_level,
            'operational_status': self.operational_status
        })

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "processing_rate_teu_per_hour": self.processing_rate_teu_per_hour,
            "berthing_capacity": self.berthing_capacity,
            "storage_capacity_teu": self.storage_capacity_teu,
            "current_congestion_level": self.current_congestion_level,
            "operational_status": self.operational_status
        })
        return data

class WarehouseNode(BaseNode):
    def __init__(self, node_id: str, name: str, 
                 capacity_sqm: float = 0.0,
                 initial_inventory_units: float = 0.0, # Simplified, could be Dict[str, float]
                 storage_cost_per_unit_day: float = 0.0,
                 operational_status: str = "OPERATIONAL",
                 **kwargs):
        super().__init__(node_id, name, node_type="Warehouse", **kwargs)
        self.capacity_sqm = capacity_sqm
        self.initial_inventory_units = initial_inventory_units
        self.storage_cost_per_unit_day = storage_cost_per_unit_day
        self.operational_status = operational_status
        self.attributes.update({
            'capacity_sqm': self.capacity_sqm,
            'initial_inventory_units': self.initial_inventory_units,
            'storage_cost_per_unit_day': self.storage_cost_per_unit_day,
            'operational_status': self.operational_status
        })

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "capacity_sqm": self.capacity_sqm,
            "initial_inventory_units": self.initial_inventory_units,
            "storage_cost_per_unit_day": self.storage_cost_per_unit_day,
            "operational_status": self.operational_status
        })
        return data

class MarketNode(BaseNode):
    def __init__(self, node_id: str, name: str, 
                 demand_rate_units_per_day: float = 0.0,
                 price_sensitivity: float = -0.1,
                 target_market_segment: str = "General",
                 operational_status: str = "OPERATIONAL",
                 **kwargs):
        super().__init__(node_id, name, node_type="Market", **kwargs)
        self.demand_rate_units_per_day = demand_rate_units_per_day
        self.price_sensitivity = price_sensitivity
        self.target_market_segment = target_market_segment
        self.operational_status = operational_status
        self.attributes.update({
            'demand_rate_units_per_day': self.demand_rate_units_per_day,
            'price_sensitivity': self.price_sensitivity,
            'target_market_segment': self.target_market_segment,
            'operational_status': self.operational_status
        })

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "demand_rate_units_per_day": self.demand_rate_units_per_day,
            "price_sensitivity": self.price_sensitivity,
            "target_market_segment": self.target_market_segment,
            "operational_status": self.operational_status
        })
        return data

class TransportHubNode(BaseNode):
    def __init__(self, node_id: str, name: str, 
                 hub_type: str = "Intermodal", # e.g., "Intermodal", "Rail", "Road", "Air"
                 transfer_capacity_units_per_hour: float = 0.0,
                 connected_modes: Optional[list[str]] = None, # e.g., ["Road", "Rail"]
                 operational_status: str = "OPERATIONAL",
                 **kwargs):
        super().__init__(node_id, name, node_type="TransportHub", **kwargs)
        self.hub_type = hub_type
        self.transfer_capacity_units_per_hour = transfer_capacity_units_per_hour
        self.connected_modes = connected_modes if connected_modes else []
        self.operational_status = operational_status
        self.attributes.update({
            'hub_type': self.hub_type,
            'transfer_capacity_units_per_hour': self.transfer_capacity_units_per_hour,
            'connected_modes': self.connected_modes,
            'operational_status': self.operational_status
        })

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "hub_type": self.hub_type,
            "transfer_capacity_units_per_hour": self.transfer_capacity_units_per_hour,
            "connected_modes": self.connected_modes,
            "operational_status": self.operational_status
        })
        return data

# Mapping from node_type string to class for dynamic instantiation
NODE_TYPE_TO_CLASS = {
    "Factory": FactoryNode,
    "Port": PortNode,
    "Warehouse": WarehouseNode,
    "Market": MarketNode,
    "TransportHub": TransportHubNode,
    # Add other types here as they are defined
}
