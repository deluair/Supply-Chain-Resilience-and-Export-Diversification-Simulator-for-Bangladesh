# Bangladesh Supply Chain Resilience and Export Diversification Simulator

This project develops an agent-based simulation model to analyze the resilience of Bangladesh's supply chains and explore strategies for export diversification. The simulator models various entities such as factories, ports, warehouses, and markets as agents or nodes within a configurable network. It allows for the introduction of disruptions and the observation of their impact on the overall system.

## Project Overview

The simulation focuses on:
- Modeling key components of Bangladesh's export-oriented supply chains.
- Simulating the flow of goods, information, and financial transactions.
- Introducing synthetic or real-world disruption scenarios (e.g., port congestion, natural disasters, policy changes).
- Assessing the impact of disruptions on metrics like export volume, lead times, and economic output.
- Providing a platform to test different mitigation and diversification strategies.

## Project Structure

```
bangladesh_supply_chain_simulator/
├── config/                     # Configuration files (e.g., config.json)
├── data/
│   ├── raw/                    # Raw input data (not versioned if large)
│   └── processed/              # Processed data for simulation input
├── docs/                       # Project documentation
├── logs/                       # Simulation logs (ignored by git)
├── notebooks/                  # Jupyter notebooks for analysis, experimentation
├── src/
│   ├── agents/                 # Agent definitions (ExportSector, Logistics, Market, Disruption)
│   ├── analysis/               # Post-simulation analysis tools (placeholder)
│   ├── data_management/        # Data loading, validation (schemas), synthetic data generation
│   ├── simulation_core/        # Core simulation engine, event manager, base agent
│   ├── supply_chain_network/   # Network model, node and edge definitions
│   ├── utils/                  # Utility functions (logger, helpers)
│   └── visualization/          # Visualization tools (placeholder)
├── tests/                      # Unit and integration tests
├── .gitignore                  # Specifies intentionally untracked files
├── main.py                     # Main script to run the simulation
├── README.md                   # This file
└── requirements.txt            # Python dependencies
```

## Setup

1.  **Prerequisites**:
    *   Python 3.9 or higher.
    *   `pip` for package installation.

2.  **Create a Virtual Environment** (recommended):
    ```bash
    python -m venv venv
    ```
    Activate the environment:
    *   Windows: `.\venv\Scripts\activate`
    *   macOS/Linux: `source venv/bin/activate`

3.  **Install Dependencies**:
    Navigate to the project root directory (`bangladesh_supply_chain_simulator`) and run:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The main simulation behavior is controlled by `config/config.json`. Key sections include:

*   `simulation_settings`: Defines total simulation steps, simulation name, random seed.
*   `logging`: Configures log levels, file paths, and rotation.
*   `network_config`:
    *   `data_source_type`: Can be "synthetic" or "file".
    *   `synthetic_params`: Parameters for generating a synthetic supply chain network (number of factories, ports, etc.).
    *   `network_data_file`: Path to a pre-defined network file if `data_source_type` is "file".
*   `agent_configs`: Specifies the number of agents of different types to create or cap.
*   `disruption_agent_default_config`: Default parameters for disruption agents.

## Usage

To run the simulation, navigate to the project root directory (`bangladesh_supply_chain_simulator`) and execute:

```bash
python main.py
```

Simulation progress and results will be logged to the file specified in `config/config.json` (default: `logs/simulation_run.log`).

## Key Modules

*   **`src/simulation_core`**: Contains the `SimulationEngine` which orchestrates the simulation, manages agents, and processes events using `simpy`.
*   **`src/agents`**: Defines the behavior of different agent types: `ExportSectorAgent`, `LogisticsAgent`, `MarketAgent`, and `DisruptionAgent`.
*   **`src/data_management`**: Handles data loading, Pydantic schemas for data validation (`schemas.py`), and the `SyntheticDataGenerator` for creating initial network and scenario data.
*   **`src/supply_chain_network`**: Defines the `SupplyChainNetwork` model using `networkx`, and the various `Node` (e.g., `FactoryNode`, `PortNode`) and `Edge` (e.g., `TransportLink`) classes.
*   **`src/utils`**: Provides common utilities like logging configuration (`logger_config.py`) and helper functions.

## Contributing

(Details to be added if contributions are expected - e.g., coding standards, pull request process.)

## License

(To be determined - e.g., MIT, Apache 2.0. Consider adding a LICENSE file.)

