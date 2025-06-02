# src/supply_chain_network/network_model.py
import networkx as nx
import logging
from typing import List, Dict, Optional, Any, Type
from .nodes import BaseNode, PortNode, FactoryNode, WarehouseNode, MarketNode, TransportHubNode # Ensure all specific node types are imported
from .edges import Edge, TransportEdge # Ensure all specific edge types are imported

logger = logging.getLogger(__name__)

class SupplyChainNetwork:
    """
    Manages the overall supply chain network structure using NetworkX.
    This class holds the graph of nodes and edges, and provides methods
    to build, modify, and query the network.
    """
    def __init__(self, name: str = "BangladeshSupplyChainNetwork"):
        self.name = name
        self.graph = nx.MultiDiGraph() # Allows multiple edges between nodes and directed edges
        self.nodes_dict: Dict[str, BaseNode] = {} # For quick lookup of Node objects by ID
        self.edges_dict: Dict[str, Edge] = {} # For quick lookup of Edge objects by ID
        logger.info(f"SupplyChainNetwork '{self.name}' initialized.")

    def add_node_object(self, node_obj: BaseNode):
        """Adds a Node object to the network."""
        if node_obj.id in self.nodes_dict:
            logger.warning(f"Node with ID {node_obj.id} ({node_obj.name}) already exists. Skipping addition.")
            return
        
        self.nodes_dict[node_obj.id] = node_obj
        # Store the object itself as 'data' attribute for easy access
        self.graph.add_node(node_obj.id, data=node_obj) 
        logger.debug(f"Added node to network: {node_obj.name} (ID: {node_obj.id})")

    def add_node(self, node_id: str, name: str, node_type: str, node_class: Type[Node] = Node, **kwargs):
        """Creates and adds a node to the network."""
        if node_id in self.nodes_dict:
            logger.warning(f"Node with ID {node_id} already exists. Skipping addition.")
            return
        
        node_obj = node_class(node_id=node_id, name=name, node_type=node_type, **kwargs)
        self.add_node_object(node_obj)


    def get_node(self, node_id: str) -> Optional[Node]:
        """Retrieves a Node object by its ID."""
        return self.nodes_dict.get(node_id)

    def add_edge_object(self, edge_obj: Edge):
        """Adds an Edge object to the network."""
        if edge_obj.id in self.edges_dict:
            logger.warning(f"Edge with ID {edge_obj.id} already exists. Skipping addition.")
            return
        if edge_obj.source_node.id not in self.nodes_dict or \
           edge_obj.destination_node.id not in self.nodes_dict:
            logger.error(f"Cannot add edge {edge_obj.id}: Source or destination node not in network.")
            return

        self.edges_dict[edge_obj.id] = edge_obj
        # Store the object itself as 'data' attribute for easy access
        self.graph.add_edge(edge_obj.source_node.id, edge_obj.destination_node.id, key=edge_obj.id, data=edge_obj)
        logger.debug(f"Added edge to network: {edge_obj.id} from {edge_obj.source_node.name} to {edge_obj.destination_node.name}")

    def add_edge(self, edge_id: str, source_node_id: str, destination_node_id: str,
                 edge_type: str, edge_class: Type[Edge] = Edge, **kwargs):
        """Creates and adds an edge to the network."""
        if edge_id in self.edges_dict:
            logger.warning(f"Edge with ID {edge_id} already exists. Skipping addition.")
            return

        source_node = self.get_node(source_node_id)
        destination_node = self.get_node(destination_node_id)

        if not source_node or not destination_node:
            logger.error(f"Cannot create edge {edge_id}: Source node '{source_node_id}' or "
                         f"destination node '{destination_node_id}' not found.")
            return
            
        edge_obj = edge_class(edge_id=edge_id, source_node=source_node,
                              destination_node=destination_node, edge_type=edge_type, **kwargs)
        self.add_edge_object(edge_obj)


    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """Retrieves an Edge object by its ID."""
        return self.edges_dict.get(edge_id)

    def get_all_nodes(self) -> List[Node]:
        return list(self.nodes_dict.values())

    def get_all_edges(self) -> List[Edge]:
        return list(self.edges_dict.values())

    def find_path(self, source_node_id: str, destination_node_id: str, weight_attribute: Optional[str] = None) -> Optional[List[str]]:
        """
        Finds a path between two nodes using NetworkX's shortest_path.
        'weight_attribute' refers to an attribute of the Edge object (e.g., 'cost_per_unit', 'base_lead_time_hours').
        Returns a list of node IDs forming the path, or None if no path exists.
        """
        if source_node_id not in self.nodes_dict or destination_node_id not in self.nodes_dict:
            logger.error(f"Source '{source_node_id}' or destination '{destination_node_id}' node not found in network.")
            return None

        try:
            if weight_attribute:
                # For NetworkX shortest_path with custom weight, the graph edges need a 'weight' attribute.
                # We'll dynamically assign it based on the edge_obj's attribute.
                def get_edge_weight(u, v, key, edge_obj_dict):
                    edge_obj = edge_obj_dict.get(key) # key is edge_id
                    if edge_obj and hasattr(edge_obj, weight_attribute):
                        val = getattr(edge_obj, weight_attribute)
                        return val if val is not None else float('inf') # Handle None weights
                    return float('inf') # Default if attribute missing or edge not found

                path_nodes = nx.shortest_path(
                    self.graph, 
                    source=source_node_id, 
                    target=destination_node_id, 
                    weight=lambda u, v, k: get_edge_weight(u, v, k, self.edges_dict)
                )
            else:
                # Unweighted path (considers number of hops)
                path_nodes = nx.shortest_path(self.graph, source=source_node_id, target=destination_node_id)
            
            logger.debug(f"Path from {source_node_id} to {destination_node_id} (weight: {weight_attribute}): {path_nodes}")
            return path_nodes
            
        except nx.NetworkXNoPath:
            logger.warning(f"No path found between {source_node_id} and {destination_node_id} with weight '{weight_attribute}'.")
            return None
        except nx.NodeNotFound: # Should be caught by the initial check, but good to have
            logger.error(f"Node not found during path calculation: {source_node_id} or {destination_node_id}")
            return None
        except Exception as e:
            logger.error(f"Error finding path for {source_node_id} -> {destination_node_id} (weight: {weight_attribute}): {e}", exc_info=True)
            return None


    def apply_disruption_to_node(self, node_id: str, disruption_details: Dict[str, Any]):
        """Applies a disruption to a specific node."""
        node = self.get_node(node_id)
        if node:
            node.update_status("DISRUPTED", disruption_details)
            logger.info(f"Applied disruption to node {node_id}: {disruption_details}")
        else:
            logger.warning(f"Cannot apply disruption: Node {node_id} not found.")

    def apply_disruption_to_edge(self, edge_id: str, disruption_details: Dict[str, Any]):
        """Applies a disruption to a specific edge."""
        edge = self.get_edge(edge_id)
        if edge:
            edge.update_status("DISRUPTED", disruption_details)
            logger.info(f"Applied disruption to edge {edge_id}: {disruption_details}")
        else:
            logger.warning(f"Cannot apply disruption: Edge {edge_id} not found.")

    def build_from_config(self, network_config_data: Dict[str, List[Dict[str, Any]]]):
        """
        Builds the network from a configuration dictionary.
        Expected format: {"nodes": [node_config1, ...], "edges": [edge_config1, ...]}
        """
        logger.info("Building supply chain network from configuration data...")
        
        node_class_map = {
            "Port": Port, "Factory": Factory, "Warehouse": Warehouse,
            "Market": MarketNode, "TransportHub": TransportHub, "Node": Node 
        }
        
        for node_data in network_config_data.get("nodes", []):
            node_id = node_data.get("id")
            name = node_data.get("name")
            node_type_str = node_data.get("node_type", "Node")
            
            if not node_id or not name:
                logger.error(f"Skipping node due to missing id or name: {node_data}")
                continue

            NodeClass = node_class_map.get(node_type_str, Node)
            node_kwargs = {k: v for k, v in node_data.items() if k not in ["id", "name", "node_type"]}
            
            # Special handling for constructor arguments that might differ from generic 'node_type'
            if NodeClass == Factory and "sector_type" not in node_kwargs and "sector_type" in node_data:
                 node_kwargs["sector_type"] = node_data["sector_type"]
            elif NodeClass == TransportHub and "hub_type" not in node_kwargs and "hub_type" in node_data:
                node_kwargs["hub_type"] = node_data["hub_type"]
            elif NodeClass == MarketNode and "demand_params" not in node_kwargs and "demand_params" in node_data:
                node_kwargs["demand_params"] = node_data["demand_params"]


            try:
                # Pass node_type_str as 'node_type' argument to the constructor
                self.add_node(node_id=node_id, name=name, node_type=node_type_str, node_class=NodeClass, **node_kwargs)
            except Exception as e:
                logger.error(f"Failed to add node {name} ({node_id}) from config: {e}", exc_info=True)

        edge_class_map = {"TransportLink": TransportLink, "Edge": Edge}

        for edge_data in network_config_data.get("edges", []):
            edge_id = edge_data.get("id")
            source_id = edge_data.get("source_node_id")
            dest_id = edge_data.get("destination_node_id")
            edge_type_str = edge_data.get("edge_type", "Edge")

            if not edge_id or not source_id or not dest_id:
                logger.error(f"Skipping edge due to missing id, source_id, or destination_id: {edge_data}")
                continue

            EdgeClass = edge_class_map.get(edge_type_str, Edge)
            edge_kwargs = {k: v for k, v in edge_data.items() if k not in ["id", "source_node_id", "destination_node_id", "edge_type"]}
            
            try:
                self.add_edge(edge_id=edge_id, source_node_id=source_id, destination_node_id=dest_id,
                              edge_type=edge_type_str, edge_class=EdgeClass, **edge_kwargs)
            except Exception as e:
                logger.error(f"Failed to add edge {edge_id} from config: {e}", exc_info=True)

        logger.info(f"Network built from config. Nodes: {len(self.nodes_dict)}, Edges: {len(self.edges_dict)}")

    def visualize(self, output_filename: Optional[str] = "network_graph.png", layout_type: str = 'spring'):
        """
        Generates a visualization of the graph using Matplotlib and NetworkX.
        Requires matplotlib to be installed.
        Layout types: 'spring', 'kamada_kawai', 'circular', 'shell', 'spectral', 'random'
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            logger.error("Matplotlib is required for network visualization. Please install it (pip install matplotlib).")
            return

        if not self.graph or self.graph.number_of_nodes() == 0:
            logger.warning("Graph is empty or not initialized, skipping visualization.")
            return

        plt.figure(figsize=(16, 12))
        
        layout_func_map = {
            'spring': nx.spring_layout, 'kamada_kawai': nx.kamada_kawai_layout,
            'circular': nx.circular_layout, 'shell': nx.shell_layout,
            'spectral': nx.spectral_layout, 'random': nx.random_layout,
        }
        pos_func = layout_func_map.get(layout_type.lower(), nx.spring_layout)
        
        try:
            pos_params = {}
            if layout_type == 'spring' and self.graph.number_of_nodes() > 0:
                 pos_params['k'] = 0.8 / (self.graph.number_of_nodes()**0.5) if self.graph.number_of_nodes() > 1 else 0.8
                 pos_params['iterations'] = 75

            pos = pos_func(self.graph, **pos_params)
        except Exception as e:
            logger.warning(f"Failed to compute '{layout_type}' layout, falling back to spring_layout. Error: {e}")
            pos = nx.spring_layout(self.graph)

        node_labels = {node_id: f"{data['data'].name}\n({data['data'].node_type})" for node_id, data in self.graph.nodes(data=True)}
        
        nx.draw(self.graph, pos, labels=node_labels, with_labels=True, node_size=3000, 
                node_color="skyblue", font_size=8, font_weight="bold", arrows=True,
                arrowstyle='-|>', arrowsize=15, width=1.5, edge_color="gray",
                connectionstyle='arc3,rad=0.1') # For MultiDiGraph, helps separate parallel edges

        edge_labels = {}
        for u, v, key, data in self.graph.edges(data=True, keys=True):
            edge_obj = data.get('data')
            if edge_obj:
                label_parts = [f"ID: {edge_obj.id}", edge_obj.edge_type]
                if isinstance(edge_obj, TransportLink):
                    label_parts.append(f"Mode: {edge_obj.mode}")
                    if edge_obj.base_lead_time_hours:
                         label_parts.append(f"LT: {edge_obj.base_lead_time_hours:.1f}h")
                edge_labels[(u, v, key)] = "\n".join(label_parts)
        
        # For MultiDiGraph, draw_networkx_edge_labels needs adjustment or careful handling
        # A simpler approach for now if complex labels are not critical for initial viz:
        simple_edge_labels = {(u,v,key): data['data'].edge_type for u,v,key,data in self.graph.edges(data=True, keys=True)}
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=simple_edge_labels, font_size=7, font_color='darkred',
                                     bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))


        plt.title(f"Supply Chain Network: {self.name} ({layout_type} layout)", fontsize=16)
        
        if output_filename:
            try:
                plt.savefig(output_filename, bbox_inches='tight', dpi=150)
                logger.info(f"Network visualization saved to {output_filename}")
            except Exception as e:
                logger.error(f"Failed to save network visualization to {output_filename}: {e}")
        else:
            logger.info("Network visualization generated but not saved (no output_filename specified).")
        plt.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    network = SupplyChainNetwork(name="TestBangladeshNetwork")

    sample_config = {
        "nodes": [
            {"id": "FAC_DHAKA_RMG", "name": "Dhaka RMG Factory", "node_type": "Factory", "sector_type": "RMG", "production_capacity_units_per_day": 500, "output_product_id": "Apparel"},
            {"id": "ICD_KAMALAPUR", "name": "ICD Kamalapur", "node_type": "TransportHub", "hub_type": "ICD", "capacity_tons_per_day": 2000},
            {"id": "PORT_CHITTAGONG", "name": "Chittagong Port", "node_type": "Port", "capacity_teu_per_day": 10000, "berth_capacity": 10},
            {"id": "MKT_EU", "name": "EU Market", "node_type": "Market", "demand_params": {"Apparel": {"base_demand": 2000}}}
        ],
        "edges": [
            {"id": "E_FAC_ICD", "source_node_id": "FAC_DHAKA_RMG", "destination_node_id": "ICD_KAMALAPUR", "edge_type": "TransportLink", "mode": "Road", "distance_km": 15, "avg_speed_kmh": 20},
            {"id": "E_ICD_PORT", "source_node_id": "ICD_KAMALAPUR", "destination_node_id": "PORT_CHITTAGONG", "edge_type": "TransportLink", "mode": "Rail", "distance_km": 320, "avg_speed_kmh": 40},
            {"id": "E_PORT_MKT", "source_node_id": "PORT_CHITTAGONG", "destination_node_id": "MKT_EU", "edge_type": "TransportLink", "mode": "Sea", "distance_km": 14000, "avg_speed_kmh": 30, "attributes": {"default_lead_time_hours": 20*24}}
        ]
    }
    network.build_from_config(sample_config)

    print(f"\nNetwork Nodes ({len(network.get_all_nodes())}):")
    for node in network.get_all_nodes():
        print(f"  - {node}")
    
    print(f"\nNetwork Edges ({len(network.get_all_edges())}):")
    for edge in network.get_all_edges():
        print(f"  - {edge}")

    path1 = network.find_path("FAC_DHAKA_RMG", "MKT_EU")
    if path1:
        print(f"\nPath (unweighted) from FAC_DHAKA_RMG to MKT_EU: {' -> '.join(path1)}")

    path2 = network.find_path("FAC_DHAKA_RMG", "MKT_EU", weight_attribute="base_lead_time_hours")
    if path2:
        print(f"\nPath (by lead time) from FAC_DHAKA_RMG to MKT_EU: {' -> '.join(path2)}")
        total_lead_time = 0
        for i in range(len(path2) - 1):
            # Find edge(s) between path2[i] and path2[i+1]
            # This is simplified; real scenario might have multiple edges or need specific edge ID
            edges_on_segment = [e for e_id, e in network.edges_dict.items() if e.source_node.id == path2[i] and e.destination_node.id == path2[i+1]]
            if edges_on_segment:
                # Assuming the first found edge is the one chosen by shortest_path, or that lead time is consistent
                edge_on_path = edges_on_segment[0] 
                if hasattr(edge_on_path, 'base_lead_time_hours'):
                    total_lead_time += edge_on_path.base_lead_time_hours
        print(f"Calculated total lead time for path: {total_lead_time:.2f} hours")


    # Visualize (ensure 'temp_visuals' directory exists or adjust path)
    import os
    output_dir = "temp_visuals"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    network.visualize(output_filename=os.path.join(output_dir, "bangladesh_network_model_example.png"))
    logger.info(f"Check for visualization in '{output_dir}' directory.")
