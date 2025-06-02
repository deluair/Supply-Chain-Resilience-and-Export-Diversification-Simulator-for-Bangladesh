# src/data_management/synthetic_data_generator.py
import random
import uuid
from typing import List, Dict, Any
from .schemas import ExportSectorSchema, LogisticsNodeSchema, MarketSchema, DisruptionSchema
import logging

logger = logging.getLogger(__name__)

class SyntheticDataGenerator:
    """
    Generates synthetic data for initializing the simulation environment
    when real data is unavailable or needs augmentation.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config if config else {}
        # Parameters for network_data generation, from network_config.synthetic_params
        self.num_factories = self.config.get("num_factories", 5)
        self.num_ports = self.config.get("num_ports", 2)
        self.num_warehouses = self.config.get("num_warehouses", 10)
        self.num_markets = self.config.get("num_markets", 20) # Note: this is for MarketNode, distinct from MarketSchema
        self.num_transport_hubs = self.config.get("num_transport_hubs", 3)
        self.connection_probability = self.config.get("connection_probability", 0.3)

        # Parameters for schema-based generation (existing methods)
        self.num_export_sectors_schema = self.config.get("num_synthetic_export_sectors", 5) 
        self.num_logistics_nodes_schema = self.config.get("num_synthetic_logistics_nodes", 10)
        self.num_markets_schema = self.config.get("num_synthetic_markets", 3)
        logger.info(f"SyntheticDataGenerator initialized with config: {self.config}")

    def generate_export_sectors(self) -> List[ExportSectorSchema]:
        sectors = []
        # Based on markdown: RMG, Pharma, Leather, ICT, Agribusiness
        example_sectors = [
            {"name": "RMG Factory", "type": "RMG", "capacity": 1000, "mat_dep": {"fabric": 2.5, "thread": 0.1}},
            {"name": "Pharma Plant", "type": "Pharmaceuticals", "capacity": 500, "mat_dep": {"chem_A": 0.5, "chem_B": 0.2}},
            {"name": "Leather Goods Unit", "type": "Leather", "capacity": 200, "mat_dep": {"raw_hide": 1.2, "dye": 0.05}},
            {"name": "ICT Firm", "type": "ICT", "capacity": 100, "mat_dep": {}}, # Different model for ICT
            {"name": "Agribusiness Processor", "type": "Agribusiness", "capacity": 300, "mat_dep": {"raw_produce": 1.5}},
        ]
        for i in range(self.num_export_sectors):
            s_data = random.choice(example_sectors)
            sector = ExportSectorSchema(
                id=uuid.uuid4(),
                name=f"{s_data['name']} {i+1}",
                sector_type=s_data['type'],
                production_capacity_units_per_day=s_data['capacity'] * random.uniform(0.8, 1.2),
                raw_material_dependency=s_data['mat_dep'],
                initial_inventory_units=random.uniform(50, 200),
                market_destinations=["EU_Market_1", "USA_Market_1"] # Placeholder
            )
            sectors.append(sector)
        logger.info(f"Generated {len(sectors)} synthetic export sectors.")
        return sectors

    def generate_logistics_nodes(self) -> List[LogisticsNodeSchema]:
        nodes = []
        node_types = ["Port", "Airport", "LandPort", "ICD", "Warehouse"]
        for i in range(self.num_logistics_nodes):
            node_type = random.choice(node_types)
            node = LogisticsNodeSchema(
                id=uuid.uuid4(),
                name=f"{node_type} Node {i+1}",
                node_type=node_type,
                capacity_teu_per_day=random.uniform(100, 1000) if node_type in ["Port", "ICD"] else None,
                capacity_tons_per_day=random.uniform(500, 5000) if node_type not in ["Port", "ICD"] else None,
                handling_time_hours=random.uniform(1, 24),
                operating_cost_per_day=random.uniform(1000, 10000),
                location_lat_lon=(random.uniform(20, 26), random.uniform(88, 92)) # Approx Bangladesh
            )
            nodes.append(node)
        logger.info(f"Generated {len(nodes)} synthetic logistics nodes.")
        return nodes

    def generate_markets(self) -> List[MarketSchema]:
        markets = []
        market_names = ["EU_Market", "USA_Market", "Asia_Emerging_Market", "MEA_Market"]
        for i in range(self.num_markets):
            market = MarketSchema(
                id=uuid.uuid4(),
                name=f"{random.choice(market_names)}_{i+1}",
                description=f"Synthetic market {i+1}",
                demand_function_params={"base_demand": random.uniform(1000, 5000), "price_elasticity": random.uniform(-0.5, -1.5)},
                trade_policies={"default_tariff": random.uniform(0.0, 0.15)}
            )
            markets.append(market)
        logger.info(f"Generated {len(markets)} synthetic markets.")
        return markets

    def generate_disruptions(self, num_disruptions=5) -> List[DisruptionSchema]:
        disruptions = []
        disruption_types = ["PoliticalInstability", "NaturalDisaster", "EnergyCrisis", "PortCongestion", "GlobalRecession"]
        target_scopes = ["Port:Chittagong", "Sector:RMG", "Region:Dhaka", "Transport:Road", "Global"]
        for i in range(num_disruptions):
            disruption = DisruptionSchema(
                id=uuid.uuid4(),
                name=f"Disruption Event {i+1}",
                disruption_type=random.choice(disruption_types),
                target_scope=random.choice(target_scopes),
                impact_parameters={"capacity_reduction_percent": random.uniform(10, 80), "duration_days": random.randint(1, 30)},
                probability_of_occurrence_per_year=random.uniform(0.01, 0.2)
            )
            disruptions.append(disruption)
        logger.info(f"Generated {len(disruptions)} synthetic disruption events.")
        return disruptions

    def generate_all_initial_data(self) -> Dict[str, List[Any]]:
        """Generates all types of synthetic data needed for simulation setup."""
        all_data = {
            "export_sectors": self.generate_export_sectors(),
            "logistics_nodes": self.generate_logistics_nodes(),
            "markets": self.generate_markets(),
            "disruptions": self.generate_disruptions(),
        }
        logger.info("Generated all initial synthetic data.")
        return all_data

if __name__ == '__main__':
    # Example usage
    generator = SyntheticDataGenerator()
    initial_data = generator.generate_all_initial_data()
    # print(f"Generated {len(initial_data['export_sectors'])} export sectors.")
    # print(f"First sector: {initial_data['export_sectors'][0].json(indent=2)}")
    # print(f"Generated {len(initial_data['logistics_nodes'])} logistics nodes.")
    # print(f"First node: {initial_data['logistics_nodes'][0].json(indent=2)}")
    # print(f"Generated {len(initial_data['markets'])} markets.")
    # print(f"First market: {initial_data['markets'][0].json(indent=2)}")
    # print(f"Generated {len(initial_data['disruptions'])} disruption events.")
    # print(f"First disruption: {initial_data['disruptions'][0].json(indent=2)}")

    # Example for new network data generation
    network_params = {
        "num_factories": 2,
        "num_ports": 1,
        "num_warehouses": 2,
        "num_markets": 3,
        "num_transport_hubs": 1,
        "connection_probability": 0.5
    }
    network_generator = SyntheticDataGenerator(config=network_params)
    nodes, edges = network_generator.generate_network_data()
    print(f"\n--- Generated Network Data ---")
    print(f"Generated {len(nodes)} nodes:")
    for node in nodes[:2]: # Print first 2 nodes
        print(json.dumps(node, indent=2, default=str))
    print(f"\nGenerated {len(edges)} edges:")
    for edge in edges[:2]: # Print first 2 edges
        print(json.dumps(edge, indent=2, default=str))
    pass

    def _generate_random_location(self):
        """Generates a random lat/lon coordinate within approximate Bangladesh bounds."""
        # Bangladesh: Lat (approx 20.0 to 26.5), Lon (approx 88.0 to 92.75)
        lat = random.uniform(20.0, 26.5)
        lon = random.uniform(88.0, 92.75)
        return (round(lat, 6), round(lon, 6))

    def generate_network_data(self) -> (List[Dict[str, Any]], List[Dict[str, Any]]):
        """
        Generates node and edge data as lists of dictionaries for building the SupplyChainNetwork.
        Uses parameters like num_factories, num_ports, etc., from self.config.
        """
        nodes_data = []
        edges_data = []
        node_objects_map = {} # Helper to store generated node objects for edge creation by ID

        node_type_counts = {
            "Factory": self.num_factories,
            "Port": self.num_ports,
            "Warehouse": self.num_warehouses,
            "MarketNode": self.num_markets,
            "TransportHub": self.num_transport_hubs
        }

        logger.info(f"Generating synthetic network data with params: {node_type_counts}")

        for node_type_str, count in node_type_counts.items():
            for i in range(count):
                node_id = str(uuid.uuid4())
                node_name = f"{node_type_str}_{i+1}"
                location = self._generate_random_location()
                node_info = {
                    "id": node_id,
                    "type": node_type_str,
                    "name": node_name,
                    "location": location,
                    "operational_status": "OPERATIONAL" # Default
                }

                if node_type_str == "Factory":
                    node_info.update({
                        "production_capacity_units_per_day": random.randint(100, 1000),
                        "raw_material_requirements": {"material_A": random.uniform(0.5, 2.0)},
                        "initial_inventory_units": random.randint(50, 200)
                    })
                elif node_type_str == "Port":
                    node_info.update({
                        "processing_rate_teu_per_hour": random.randint(20, 100),
                        "berthing_capacity": random.randint(1, 5),
                        "storage_capacity_teu": random.randint(1000, 5000),
                        "current_congestion_level": random.uniform(0.0, 0.3)
                    })
                elif node_type_str == "Warehouse":
                    node_info.update({
                        "capacity_sqm": random.randint(1000, 10000),
                        "initial_inventory_units": random.randint(100, 500),
                        "storage_cost_per_unit_day": random.uniform(0.1, 0.5)
                    })
                elif node_type_str == "MarketNode":
                    node_info.update({
                        "demand_rate_units_per_day": random.randint(50, 500),
                        "price_sensitivity": random.uniform(-0.5, -0.1) # Example value
                    })
                elif node_type_str == "TransportHub":
                    node_info.update({
                        "hub_type": random.choice(["Road", "Rail", "Intermodal"]),
                        "transfer_capacity_units_per_hour": random.randint(50, 200),
                        "connected_modes": ["Road", "Rail"] # Example
                    })
                
                nodes_data.append(node_info)
                node_objects_map[node_id] = node_info # Store for edge creation

        logger.info(f"Generated {len(nodes_data)} nodes for the network.")

        # Define plausible connections between node types (Source Type -> List of Target Types)
        plausible_connections = {
            "Factory": ["Port", "Warehouse", "TransportHub"],
            "Port": ["Warehouse", "TransportHub", "MarketNode"],
            "Warehouse": ["TransportHub", "MarketNode", "Factory"], # Warehouse can supply back to factory
            "TransportHub": ["Port", "Warehouse", "MarketNode", "Factory"],
            "MarketNode": [] # Markets are typically destinations
        }

        all_node_ids = list(node_objects_map.keys())
        if len(all_node_ids) < 2: # Need at least two nodes to form an edge
            logger.warning("Not enough nodes to generate edges.")
            return nodes_data, edges_data

        for source_id in all_node_ids:
            source_node_info = node_objects_map[source_id]
            source_type = source_node_info["type"]
            
            possible_target_types = plausible_connections.get(source_type, [])
            if not possible_target_types:
                continue

            for target_id in all_node_ids:
                if source_id == target_id: # No self-loops for now
                    continue
                
                target_node_info = node_objects_map[target_id]
                target_type = target_node_info["type"]

                if target_type in possible_target_types:
                    if random.random() < self.connection_probability:
                        edge_id = str(uuid.uuid4())
                        edge_info = {
                            "id": edge_id,
                            "source_id": source_id,
                            "target_id": target_id,
                            "mode": random.choice(["Road", "Rail", "Sea", "Air"]),
                            "capacity_units_per_day": random.randint(50, 500),
                            "cost_per_unit": random.uniform(1, 10),
                            "distance_km": random.uniform(10, 500), # Simplified
                            "lead_time_hours": random.uniform(1, 48),
                            "current_flow_units_per_day": 0,
                            "operational_status": "OPERATIONAL"
                        }
                        edges_data.append(edge_info)
        
        logger.info(f"Generated {len(edges_data)} edges for the network based on probability {self.connection_probability}.")
        return nodes_data, edges_data
import json # For the __main__ example
