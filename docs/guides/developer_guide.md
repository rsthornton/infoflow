# InfoFlow Developer Guide

This guide provides comprehensive information for developers who want to work with, extend, or modify the InfoFlow simulation system.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Adding New Features](#adding-new-features)
5. [Testing](#testing)
6. [Contribution Guidelines](#contribution-guidelines)
7. [Common Patterns](#common-patterns)
8. [API Reference](#api-reference)

## Development Environment Setup

### Prerequisites

- Python 3.11 or higher
- Git for version control
- A good IDE (recommended: Visual Studio Code or PyCharm)

### Setting Up a Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/infoflow.git
cd infoflow
```

2. Set up a virtual environment:
```bash
# Using venv
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# OR using conda
conda env create -f config/environment.yml
conda activate infoflow
```

3. Install in development mode:
```bash
pip install -e .
```

This installs the package in development mode, allowing you to modify the code without reinstalling.

4. Install development dependencies:
```bash
pip install -r config/dev-requirements.txt
```

### Development Tools

- **Testing**: pytest
- **Linting**: flake8, black, pylint
- **Type checking**: mypy (optional)
- **Documentation**: Markdown

## Project Structure

The project follows a modular structure that separates different aspects of the simulation:

### Core Modules

- `infoflow/core/model.py`: The main simulation model
- `infoflow/core/network.py`: Network creation and analysis utilities
- `infoflow/agents/base.py`: Base agent classes
- `infoflow/agents/media/`: Specialized media agent implementations
- `infoflow/data/`: Data collection and analysis tools
- `infoflow/utils/`: Utility functions and helpers
- `infoflow/web/`: Web interface components

### Entry Points

- `run_server.py`: Starts the web interface
- `run_tests.py`: Runs the test suite
- `verify_setup.py`: Verifies the installation

### Configuration

- `config/requirements.txt`: Production dependencies
- `config/environment.yml`: Conda environment specification

## Core Components

### The Model Class

The `InformationFlowModel` class (in `infoflow/core/model.py`) is the central component of the simulation. It:

- Initializes the network structure
- Creates and manages agents
- Coordinates simulation steps
- Collects and processes data

Key methods:

```python
def __init__(self, **parameters):
    """Initialize the model with parameters."""
    # ...

def _create_network(self):
    """Create the network structure."""
    # ...

def _create_citizen_agents(self):
    """Create and place citizen agents."""
    # ...

def _create_media_agents(self):
    """Create media agents of different types."""
    # ...

def step(self):
    """Execute one step of the simulation."""
    # ...
```

### Agent Classes

Agents are defined in the `infoflow/agents/` directory. The hierarchy is:

- `BaseAgent`: Foundation for all agents
  - `CitizenAgent`: Represents individuals in the network
  - `SocialMediaAgent`: Base class for media sources
    - `CorporateMediaAgent`: Traditional media
    - `InfluencerAgent`: Social media influencers
    - `GovernmentMediaAgent`: Government sources

Key agent methods:

```python
def step(self):
    """Execute the agent's behavior for one step."""
    # ...

def receive_information(self, content, source):
    """Process received information."""
    # ...

def share_information(self):
    """Share information with connected agents."""
    # ...

def update_trust(self, source_type, perceived_accuracy):
    """Update trust in a source based on content accuracy."""
    # ...
```

### Network Structure

Networks are created using the functions in `infoflow/core/network.py`, which provides:

- Small-world network creation
- Scale-free network creation
- Random network creation
- Helper functions for network analysis

### Data Collection

Data collection is handled by:

1. Mesa's built-in `DataCollector` class
2. Custom `StatsCollector` in `infoflow/utils/simple_stats.py`
3. Visualization utilities in `infoflow/data/visualization.py`

## Adding New Features

### Adding a New Agent Type

To add a new agent type:

1. Identify which base class to extend (`BaseAgent`, `CitizenAgent`, or `SocialMediaAgent`)
2. Create a new file in the appropriate directory (e.g., `infoflow/agents/specialized/new_agent.py`)
3. Define your agent class:

```python
from infoflow.agents.base import CitizenAgent

class SpecializedCitizenAgent(CitizenAgent):
    """A specialized citizen agent with custom behavior."""
    
    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
        self.special_attribute = kwargs.get('special_attribute', 0)
    
    def specialized_method(self):
        """Implement specialized behavior."""
        # Your implementation here
    
    def step(self):
        """Override the step method if needed."""
        # Custom logic
        super().step()  # Call parent method if needed
        # Additional custom logic
```

4. Update the model to use your new agent type:

```python
# In infoflow/core/model.py

from infoflow.agents.specialized.new_agent import SpecializedCitizenAgent

class InformationFlowModel(mesa.Model):
    # ...
    
    def _create_specialized_agents(self):
        """Create specialized agents."""
        for i in range(self.num_specialized):
            agent = SpecializedCitizenAgent(
                model=self,
                # ... parameters
            )
            # Place agent in network
            # ...
```

### Adding a New Network Type

To add a new network structure:

1. Add a new function to `infoflow/core/network.py`:

```python
def create_clustered_network(
    num_nodes: int,
    num_clusters: int,
    p_within: float,
    p_between: float,
    seed: Optional[int] = None
) -> nx.Graph:
    """
    Create a clustered network with dense connections within clusters
    and sparse connections between clusters.
    
    Args:
        num_nodes: Number of nodes
        num_clusters: Number of clusters
        p_within: Probability of connection within a cluster
        p_between: Probability of connection between clusters
        seed: Random seed
        
    Returns:
        A networkx graph with clustered structure
    """
    G = nx.Graph()
    G.add_nodes_from(range(num_nodes))
    
    # Assign nodes to clusters
    nodes_per_cluster = num_nodes // num_clusters
    clusters = {}
    for i in range(num_clusters):
        start = i * nodes_per_cluster
        end = (i + 1) * nodes_per_cluster if i < num_clusters - 1 else num_nodes
        clusters[i] = list(range(start, end))
    
    # Add edges within clusters (higher probability)
    for cluster_nodes in clusters.values():
        for i in range(len(cluster_nodes)):
            for j in range(i + 1, len(cluster_nodes)):
                if random.random() < p_within:
                    G.add_edge(cluster_nodes[i], cluster_nodes[j])
    
    # Add edges between clusters (lower probability)
    for i in range(num_clusters):
        for j in range(i + 1, num_clusters):
            for node_i in clusters[i]:
                for node_j in clusters[j]:
                    if random.random() < p_between:
                        G.add_edge(node_i, node_j)
    
    return G
```

2. Update the `create_network` function to include your new network type:

```python
def create_network(
    network_type: str,
    num_nodes: int,
    params: Dict[str, Any],
    seed: Optional[int] = None
) -> nx.Graph:
    """Create a network of the specified type."""
    # ...existing code...
    
    elif network_type == "clustered":
        return create_clustered_network(
            num_nodes=num_nodes,
            num_clusters=params.get("clustered_num_clusters", 3),
            p_within=params.get("clustered_p_within", 0.3),
            p_between=params.get("clustered_p_between", 0.05),
            seed=seed
        )
    # ...rest of the function...
```

3. Update the model parameters to include the new network type:

```python
# In infoflow/core/model.py

def __init__(self, network_type="small_world", **kwargs):
    # ...
    
    self.network_params = network_params or {
        "small_world_k": 4,
        "small_world_p": 0.1,
        "scale_free_m": 3,
        "random_p": 0.1,
        # Add new network parameters
        "clustered_num_clusters": 3,
        "clustered_p_within": 0.3,
        "clustered_p_between": 0.05
    }
    
    # ...
```

### Adding New Metrics

To add new metrics for data collection:

1. Define new functions in `infoflow/data/metrics.py`:

```python
def calculate_polarization(truth_assessments):
    """
    Calculate polarization as bimodality of truth assessments.
    
    Higher values indicate more polarization (split opinions).
    Lower values indicate consensus.
    
    Args:
        truth_assessments: List of truth assessment values
        
    Returns:
        Polarization metric (0-1 scale)
    """
    import numpy as np
    from scipy.stats import gaussian_kde
    
    # Need at least 3 values for meaningful density estimation
    if len(truth_assessments) < 3:
        return 0
    
    # Kernel density estimation
    kde = gaussian_kde(truth_assessments)
    
    # Evaluate density at points
    x = np.linspace(0, 1, 100)
    density = kde(x)
    
    # Normalize density
    density = density / np.max(density)
    
    # Find peaks (local maxima)
    peaks = []
    for i in range(1, len(x) - 1):
        if density[i] > density[i-1] and density[i] > density[i+1]:
            peaks.append((x[i], density[i]))
    
    # If there's only one peak, there's no polarization
    if len(peaks) <= 1:
        return 0
    
    # Sort peaks by height
    peaks.sort(key=lambda p: p[1], reverse=True)
    
    # Take the two highest peaks
    peak1, peak2 = peaks[0], peaks[1]
    
    # Polarization is a function of:
    # 1. Distance between peaks (farther = more polarized)
    # 2. Height of the smaller peak (higher = more polarized)
    distance = abs(peak1[0] - peak2[0])
    relative_height = peak2[1] / peak1[1]
    
    # Combined metric (0-1 scale)
    polarization = (distance * relative_height) 
    
    return min(1.0, polarization)
```

2. Update the model's data collection setup:

```python
# In infoflow/core/model.py

def _setup_data_collection(self):
    """Set up data collection for the model."""
    # ...existing code...
    
    self.datacollector = mesa.DataCollector(
        # Model-level metrics
        model_reporters={
            # ...existing metrics...
            "Polarization": lambda m: calculate_polarization([a.truth_assessment for a in m.citizens]),
        },
        # ...rest of the function...
    )
```

## Testing

### Running Tests

The project uses pytest for testing. To run the tests:

```bash
# Run all tests
python run_tests.py

# Run specific test file
pytest tests/test_model.py

# Run tests with coverage
pytest --cov=infoflow tests/
```

### Writing Tests

When adding new features, always add corresponding tests:

1. Create or modify a test file in the `tests/` directory
2. Follow the existing test patterns
3. Use descriptive test names that explain what is being tested

Example test:

```python
# tests/test_new_feature.py

import pytest
from infoflow.core.model import create_model
from infoflow.agents.specialized.new_agent import SpecializedCitizenAgent

def test_specialized_agent_creation():
    """Test that specialized agents are created correctly."""
    # Setup
    model = create_model(num_specialized=5)
    
    # Check there are specialized agents
    specialized_agents = [a for a in model.agents 
                          if isinstance(a, SpecializedCitizenAgent)]
    assert len(specialized_agents) == 5
    
    # Test properties
    for agent in specialized_agents:
        assert hasattr(agent, "special_attribute")
        assert 0 <= agent.special_attribute <= 10

def test_specialized_behavior():
    """Test that specialized behavior works correctly."""
    # Setup
    model = create_model(num_specialized=1)
    specialized_agent = next(a for a in model.agents 
                            if isinstance(a, SpecializedCitizenAgent))
    
    # Save initial state
    initial_value = specialized_agent.truth_assessment
    
    # Run the specialized method
    specialized_agent.specialized_method()
    
    # Check that the method had the expected effect
    assert specialized_agent.truth_assessment != initial_value
```

## Contribution Guidelines

### Code Style

The project uses the following code style guidelines:

- Use Black for formatting
- Follow PEP 8 conventions
- Use type hints whenever possible
- Write docstrings for all functions, classes, and methods

Format your code with:

```bash
black infoflow/
```

Lint your code with:

```bash
flake8 infoflow/
```

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Run the tests to ensure they pass
5. Format your code
6. Commit your changes (`git commit -m 'Add new feature'`)
7. Push to your fork (`git push origin feature/new-feature`)
8. Open a Pull Request

### Documentation

When adding new features:

1. Update docstrings in the code
2. Update relevant documentation files
3. Add examples of how to use the new feature
4. Document any new parameters or return values

## Common Patterns

### Creating Agents

The standard pattern for creating agents:

```python
agent = AgentClass(
    model=self,  # Reference to the model
    param1=value1,
    param2=value2
)

# For citizen agents, place them in the network
self.grid.place_agent(agent, node_id)
```

### Processing Agent Lists

Use Mesa's AgentSet for efficient agent operations:

```python
# Create an agent set
from mesa.agent import AgentSet
agent_set = AgentSet(agent_list, random=self.random)

# Perform operations on all agents
agent_set.do("method_name", arg1, arg2)

# Apply a filter
filtered_agents = agent_set.filter(lambda a: a.attribute > threshold)
```

### Content Distribution Pattern

Media agents follow this pattern:

```python
def step(self):
    """Execute one step."""
    # Decide whether to publish
    content = self.publish_content()
    
    # If content was created, distribute it
    if content:
        recipients = self.broadcast_content(content)
```

And citizen agents:

```python
def step(self):
    """Execute one step."""
    # Process social influence
    self.be_influenced_by_network()
    
    # Share information
    content = self.share_information()
    if content:
        for neighbor in self.neighbors:
            neighbor.receive_information(content, self)
    
    # Seek information
    self.seek_information()
```

### Data Collection Pattern

For collecting metric data:

```python
# In model initialization
self.datacollector = mesa.DataCollector(
    model_reporters={
        "Metric1": lambda m: calculate_metric1(m),
        "Metric2": lambda m: np.mean([a.attribute for a in m.agents])
    },
    agent_reporters={
        "Attribute1": lambda a: getattr(a, "attribute1", None)
    }
)

# In model step method
def step(self):
    """Execute one step."""
    # Agent steps
    # ...
    
    # Collect data after the step
    self.datacollector.collect(self)
    
    # Record additional metrics
    self._record_stats()
```

## API Reference

For the complete API reference, see the documentation files in the `docs/api/` directory.