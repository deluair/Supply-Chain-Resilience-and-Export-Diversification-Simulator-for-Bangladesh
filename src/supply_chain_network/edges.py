# src/supply_chain_network/edges.py
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Edge:
    """
    Represents a generic edge (link) in the supply chain network graph.
    Connects two nodes (source_node_id, target_node_id).
    """
    def __init__(self, source_node_id: str, target_node_id: str, edge_type: str,
                 capacity: Optional[float] = None, # e.g., TEUs/day, tons/day
                 travel_time_hours: Optional[float] = None,
                 cost_per_unit: Optional[float] = None,
                 attributes: Optional[Dict[str, Any]] = None):
        self.source_id: str = source_node_id
        self.target_id: str = target_node_id
        self.type: str = edge_type # e.g., "Road", "Sea", "Rail", "Air", "Contract"
        self.capacity: Optional[float] = capacity
        self.travel_time_hours: Optional[float] = travel_time_hours
        self.cost_per_unit: Optional[float] = cost_per_unit # Cost per unit transported
        self.attributes: Dict[str, Any] = attributes if attributes else {}
        # Operational status, can be affected by disruptions
        self.is_active: bool = True
        self.current_flow: float = 0.0

        logger.debug(f"Edge created: {self.source_id} -> {self.target_id} (type: {self.type})")

    def __repr__(self):
        return f"<Edge({self.source_id} -> {self.target_id}, type='{self.type}', cap={self.capacity})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type,
            "capacity": self.capacity,
            "travel_time_hours": self.travel_time_hours,
            "cost_per_unit": self.cost_per_unit,
            "is_active": self.is_active,
            "current_flow": self.current_flow,
            "attributes": self.attributes,
        }

# Example specific edge types
class TransportEdge(Edge):
    def __init__(self, source_node_id: str, target_node_id: str, transport_mode: str, **kwargs):
        # transport_mode could be "Road", "Sea", "Rail", "Air"
        super().__init__(source_node_id, target_node_id, edge_type=f"Transport::{transport_mode}", **kwargs)
        self.attributes['mode'] = transport_mode
        # e.g., self.attributes['distance_km'] = 100

class ContractualEdge(Edge):
    def __init__(self, source_node_id: str, target_node_id: str, contract_type: str, **kwargs):
        # contract_type could be "SupplyAgreement", "ServiceLevelAgreement"
        super().__init__(source_node_id, target_node_id, edge_type=f"Contract::{contract_type}", **kwargs)
        self.attributes['contract_terms'] = kwargs.get('contract_terms', {})
        # This type of edge might not have 'travel_time' but 'lead_time' or 'response_time'
