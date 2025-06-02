# src/data_management/schemas.py
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
import uuid

class BaseSchema(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    description: Optional[str] = None

class ExportSectorSchema(BaseSchema):
    sector_type: str # e.g., RMG, Pharmaceuticals, Leather
    production_capacity_units_per_day: float
    raw_material_dependency: Dict[str, float] # item: quantity_needed_per_unit
    initial_inventory_units: float = 0.0
    market_destinations: List[str] # e.g., ["EU", "USA"]

class LogisticsNodeSchema(BaseSchema):
    node_type: str # e.g., "Port", "Airport", "LandPort", "ICD", "Warehouse"
    capacity_teu_per_day: Optional[float] = None # For ports/ICDs
    capacity_tons_per_day: Optional[float] = None # For other transport/warehousing
    handling_time_hours: float
    operating_cost_per_day: float
    location_lat_lon: Optional[tuple[float, float]] = None
    connected_nodes: List[uuid.UUID] = []

class MarketSchema(BaseSchema):
    market_name: str # e.g., "EU", "USA", "Asia_Emerging"
    demand_function_params: Dict[str, Any] # Parameters for demand model
    trade_policies: Dict[str, Any] # e.g., tariffs, quotas per product type

class DisruptionSchema(BaseSchema):
    disruption_type: str # e.g., "PoliticalInstability", "NaturalDisaster", "EnergyCrisis"
    target_scope: str # e.g., "Port:Chittagong", "Sector:RMG", "Region:Dhaka"
    impact_parameters: Dict[str, Any] # e.g., {"capacity_reduction_percent": 50, "duration_days": 7}
    probability_of_occurrence_per_year: float = Field(..., ge=0, le=1)

class TradeDataSchema(BaseModel):
    year: int
    exporting_country: str = "Bangladesh"
    importing_country: str
    product_hscode: str
    product_description: str
    value_usd: float
    quantity_kg: Optional[float] = None

class PortDataSchema(BaseModel):
    port_name: str
    date: str # YYYY-MM-DD
    vessels_at_berth: int
    vessels_waiting: int
    avg_berthing_delay_hours: float
    yard_occupancy_percent: float
    customs_clearance_rate_percent: float

# Add more schemas as needed based on the markdown's data requirements.
