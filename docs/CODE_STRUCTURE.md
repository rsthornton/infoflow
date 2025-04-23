# InfoFlow Code Structure

This document provides an overview of the InfoFlow codebase, describing the purpose and components of each module.

> **Note**: For information on managing simulation runs and data, see [Managing Simulations](guides/managing_simulations.md).

## Package Structure

```
infoflow/
├── __init__.py             # Package exports
├── agents/                 # Agent implementations
├── core/                   # Core model components
├── data/                   # Data collection and analysis
├── utils/                  # Utility functions
└── web/                    # Flask web application
```

## Agents Package

The `agents` package contains all agent-related implementations.

### agents/base.py

Contains the following main classes:

- `BaseAgent`: Abstract base class for all agent types
- `CitizenAgent`: Implementation of citizen agents who consume, process, and share information
  - Key methods:
    - `receive_information()`: Processes incoming information
    - `update_trust()`: Updates trust in different source types
    - `share_information()`: Decides whether and what to share
    - `be_influenced_by_network()`: Updates truth assessments based on network connections
    - `seek_information()`: Actively seeks new information (for truth-seeking agents)
- `SocialMediaAgent`: Base class for all social media agent types
  - Key methods:
    - `create_content()`: Creates content based on agent properties
    - `publish_content()`: Decides whether to publish content this step
    - `broadcast_content()`: Distributes content to appropriate citizen agents

### agents/media/

Contains specialized media agent implementations:

- **base.py**: Extended functionality for social media agents
- **corporate.py**: `CorporateMediaAgent` with high authority and wide reach
- **influencer.py**: `InfluencerAgent` with follower management and engagement
- **government.py**: `GovernmentMediaAgent` with high authority and influence

## Core Package

The `core` package contains the central model implementation and network utilities.

### core/model.py

Contains the main simulation model:

- `InformationFlowModel`: Core model for information flow simulation
  - Key methods:
    - `__init__()`: Sets up the model with given parameters
    - `_create_network()`: Creates a network of the specified type
    - `_create_citizen_agents()`: Creates and places citizen agents in the network
    - `_create_media_agents()`: Creates media agents of different types
    - `_setup_data_collection()`: Sets up data collection for the model
    - `setup_connections()`: Sets up all network connections after agents are created
    - `step()`: Executes one step of the model
- `create_model()`: Helper function to quickly create a model with standard parameters

### core/network.py

Contains utilities for network generation and analysis:

- Functions for creating different network types
- Network analysis metrics
- Visualization utilities for networks

## Data Package

The `data` package handles data collection, metrics calculation, and visualization.

### data/collectors.py

- `DataCollector`: Collects and stores simulation data
  - Key methods:
    - `collect_truth_assessment_metrics()`: Collects metrics related to truth assessment distribution
    - `collect_trust_metrics()`: Collects metrics related to trust levels
    - `collect_all()`: Collects all metrics

### data/metrics.py

Contains metric definitions and calculations:

- `calculate_polarization()`: Calculates polarization index based on truth assessment distribution
- `calculate_opinion_clusters()`: Calculates the number of opinion clusters in the population
- `calculate_truth_correlation()`: Calculates correlation between agent truth assessments and actual truth values

### data/visualization.py

Contains visualization utilities:

- Functions for creating different types of visualizations
- Integration with plotting libraries
- Helper functions for formatting data for visualization

## Utils Package

The `utils` package contains utility functions used throughout the codebase.

### utils/helpers.py

Contains general utility functions:

- Mathematical helpers
- Data processing utilities
- Common validation functions

## Web Package

The `web` package contains the Flask web application components.

### web/__init__.py

Contains the Flask application factory:

- `create_app()`: Creates and configures the Flask application

### web/routes.py

Contains the Flask routes:

- `index()`: Renders the main page
- `simulation()`: Renders the simulation page
- `run_simulation()`: API endpoint for running a simulation

### web/templates/

Contains HTML templates:

- `base.html`: Base template with common layout
- `index.html`: Main landing page
- `simulation.html`: Interactive simulation page

## Entry Points

The project has several entry points:

- `run_server.py`: Runs the Flask web server
- `run_tests.py`: Runs the test suite
- `verify_setup.py`: Verifies the installation
- `setup.py`: Installation script
- `delete_runs.py`: Utility for managing simulation runs

## Testing

Tests are organized in the `tests/` directory:

- `test_agent_behavior.py`: Tests for agent behaviors
- `test_base_agents.py`: Tests for base agent functionality
- `test_model.py`: Tests for the model implementation
- `test_political_bias.py`: Tests for political bias implementation