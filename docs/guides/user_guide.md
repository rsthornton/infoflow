# InfoFlow User Guide

This guide provides comprehensive information on using the InfoFlow simulation system. It covers everything from basic setup to advanced simulation techniques.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [Running Your First Simulation](#running-your-first-simulation)
4. [Web Interface Guide](#web-interface-guide)
5. [Configuration Parameters](#configuration-parameters)
6. [Analyzing Results](#analyzing-results)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)

## Getting Started

InfoFlow is an agent-based simulation framework for studying how information flows through social networks and how truth assessments evolve based on agent interactions. The system models:

- Various types of citizens with different cognitive characteristics
- Different media sources (corporate, influencer, government) 
- Network structures that connect agents
- Trust dynamics between agents and information sources
- Evolution of truth assessments over time

## Installation

### Prerequisites

- Python 3.11 or higher
- Git (for cloning the repository)
- pip or conda (for package management)

### Option 1: Using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/infoflow.git
cd infoflow

# Create a virtual environment
python -m venv env

# Activate the environment
# On Windows:
env\Scripts\activate
# On macOS/Linux:
source env/bin/activate

# Install dependencies
pip install -r config/requirements.txt

# Install in development mode (optional)
pip install -e .
```

### Option 2: Using conda

```bash
# Clone the repository
git clone https://github.com/yourusername/infoflow.git
cd infoflow

# Create a conda environment from the environment file
conda env create -f config/environment.yml

# Activate the environment
conda activate infoflow
```

### Verifying Your Installation

To verify that your installation is working correctly:

```bash
python verify_setup.py
```

This script checks that all required dependencies are installed and that the core functionality is working.

## Running Your First Simulation

### Using the Web Interface

The simplest way to run a simulation is through the web interface:

1. Start the web server:
   ```bash
   python run_server.py
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5001
   ```

3. Click on "Run Simulation" in the navigation menu
4. Configure your simulation parameters (or use the defaults)
5. Click "Run Simulation" to start the simulation
6. View the results in the visualization tabs

### Using the Python API

You can also run simulations programmatically:

```python
from infoflow.core.model import create_model

# Create a model with default parameters
model = create_model()

# Run the simulation for 50 steps
for _ in range(50):
    model.step()

# Access the results
results = model.datacollector.get_model_vars_dataframe()
print(results.head())
```

## Web Interface Guide

The web interface consists of several pages:

### Home Page

- Overview of the project
- Links to different sections
- Quick start options

### Run Simulation

This page allows you to:

- Configure all simulation parameters
- Run simulations with different settings
- View real-time results
- Save simulation results for later analysis

The interface is organized into parameter groups:

1. **Basic Setup**
   - Number of citizens
   - Number and types of media agents
   - Network structure

2. **Agent Parameters**
   - Citizen cognitive attributes
   - Media agent characteristics
   - Trust initialization

3. **Network Parameters**
   - Network topology settings
   - Connection properties

4. **Run Controls**
   - Number of steps
   - Random seed
   - Simulation name

### Simulation History

This page lets you:

- View past simulation runs
- Compare results between different parameter sets
- Export data for external analysis
- Generate plots and visualizations

## Configuration Parameters

### Basic Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `num_citizens` | Number of citizen agents | 50 | 10-1000 |
| `num_corporate_media` | Number of corporate media agents | 3 | 0-20 |
| `num_influencers` | Number of influencer agents | 5 | 0-50 |
| `num_government` | Number of government media agents | 1 | 0-5 |
| `network_type` | Type of network structure | "small_world" | "small_world", "scale_free", "random" |
| `seed` | Random seed for reproducibility | None | Any integer |

### Citizen Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `truth_seeking_mean` | Mean of truth seeking distribution | 0 | -5 to 5 |
| `truth_seeking_std` | Standard deviation of truth seeking | 2.5 | 0 to 5 |
| `confirmation_bias_min` | Minimum confirmation bias | 3 | 0 to 10 |
| `confirmation_bias_max` | Maximum confirmation bias | 8 | 0 to 10 |
| `critical_thinking_min` | Minimum critical thinking | 3 | 0 to 10 |
| `critical_thinking_max` | Maximum critical thinking | 8 | 0 to 10 |
| `social_conformity_min` | Minimum social conformity | 3 | 0 to 10 |
| `social_conformity_max` | Maximum social conformity | 8 | 0 to 10 |
| `initial_trust_in_corporate` | Initial trust in corporate media | 5.0 | 0 to 10 |
| `initial_trust_in_influencers` | Initial trust in influencers | 5.0 | 0 to 10 |
| `initial_trust_in_government` | Initial trust in government | 5.0 | 0 to 10 |

### Media Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `corporate_bias_min` | Minimum corporate media bias | -3 | -5 to 5 |
| `corporate_bias_max` | Maximum corporate media bias | 3 | -5 to 5 |
| `influencer_bias_min` | Minimum influencer bias | -4 | -5 to 5 |
| `influencer_bias_max` | Maximum influencer bias | 4 | -5 to 5 |
| `government_bias` | Government media bias | 1.0 | -5 to 5 |
| `truth_commitment_corporate` | Truth commitment for corporate media | 6.0 | 0 to 10 |
| `truth_commitment_influencer` | Truth commitment for influencers | 4.0 | 0 to 10 |
| `truth_commitment_government` | Truth commitment for government | 5.0 | 0 to 10 |
| `corporate_publication_rate` | Publication rate for corporate media | 0.8 | 0 to 1 |
| `corporate_influence_reach` | Reach for corporate media | 0.7 | 0 to 1 |
| `influencer_publication_rate` | Publication rate for influencers | 0.9 | 0 to 1 |
| `influencer_influence_reach` | Reach for influencers | 0.5 | 0 to 1 |
| `government_publication_rate` | Publication rate for government | 0.7 | 0 to 1 |
| `government_influence_reach` | Reach for government | 0.6 | 0 to 1 |

### Network Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `small_world_k` | Number of neighbors in small world network | 4 | 2-10 |
| `small_world_p` | Rewiring probability in small world network | 0.1 | 0-1 |
| `scale_free_m` | New edges in scale-free network | 3 | 1-10 |
| `random_p` | Connection probability in random network | 0.1 | 0-1 |

## Analyzing Results

The system provides several ways to analyze simulation results:

### Through the Web Interface

1. Go to the "Simulation History" page
2. Select the simulation run(s) you want to analyze
3. Use the visualization tools to:
   - Plot truth assessment evolution
   - Visualize trust dynamics
   - Examine network structure
   - Compare runs with different parameters

### Using Analysis Scripts

InfoFlow includes several analysis scripts:

```bash
# List recent simulation runs
python scripts/compare_runs.py --list

# Compare specific metrics between runs
python scripts/compare_runs.py RUN_ID1 RUN_ID2 --metric avg_trust_government

# Generate a full analysis report
python scripts/compare_runs.py RUN_ID --report

# Export simulation data to JSON
python scripts/compare_runs.py --export RUN_ID
```

### Direct Data Access

You can also access the simulation data directly:

```python
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('data/simulation_stats.db')

# Query simulation runs
runs = pd.read_sql("SELECT * FROM simulation_runs", conn)
print(runs)

# Get data for a specific run
run_id = "your_run_id"
data = pd.read_sql(f"SELECT * FROM simulation_data WHERE run_id = '{run_id}'", conn)
print(data)

# Close the connection
conn.close()
```

## Advanced Usage

### Running Batch Simulations

For systematic parameter exploration:

```python
from infoflow.core.model import create_model
import pandas as pd
import itertools

# Define parameter ranges to explore
parameters = {
    'truth_seeking_mean': [-2, 0, 2],
    'government_bias': [-3, 0, 3],
    'network_type': ['small_world', 'scale_free']
}

# Generate all combinations
combinations = list(itertools.product(*parameters.values()))
param_names = list(parameters.keys())

results = []

# Run simulations for each combination
for combo in combinations:
    params = dict(zip(param_names, combo))
    
    # Create model with these parameters
    model = create_model(**params)
    
    # Run for 50 steps
    for _ in range(50):
        model.step()
    
    # Get final metrics
    final_data = model.datacollector.get_model_vars_dataframe().iloc[-1].to_dict()
    
    # Add parameters to results
    result = {**params, **final_data}
    results.append(result)

# Analyze results
results_df = pd.DataFrame(results)
print(results_df)
```

### Custom Network Structures

You can create custom network structures:

```python
import networkx as nx
from infoflow.core.model import InformationFlowModel

# Create a custom network
def create_custom_network(num_nodes):
    G = nx.Graph()
    G.add_nodes_from(range(num_nodes))
    
    # Add a central hub with connections to all nodes
    for i in range(1, num_nodes):
        G.add_edge(0, i)
    
    # Add some random edges
    for i in range(10):
        a = random.randint(1, num_nodes-1)
        b = random.randint(1, num_nodes-1)
        if a != b:
            G.add_edge(a, b)
    
    return G

# Create a model with this network
model = InformationFlowModel(num_citizens=50)

# Override the network with custom one
model.G = create_custom_network(50)
model.grid = mesa.space.NetworkGrid(model.G)

# Now create agents and run simulation
model._create_citizen_agents()
model._create_media_agents()
# ... rest of initialization
```

## Troubleshooting

### Common Issues

#### Web Interface Not Starting

**Symptom**: `run_server.py` exits with an error about port being in use

**Solution**: Change the port number:
```bash
python run_server.py --port 5002
```

#### Out of Memory Errors

**Symptom**: You get a memory error when running large simulations

**Solution**: Reduce the number of agents or steps, or use a more memory-efficient approach:
```python
# Use smaller batches
model = create_model(num_citizens=200)

# Process in chunks of 10 steps
for chunk in range(5):
    for _ in range(10):
        model.step()
    
    # Analyze intermediate results
    results = model.datacollector.get_model_vars_dataframe()
    # ... save or process results
    
    # Optionally clear datacollector to save memory
    model.datacollector.model_vars = {}
```

#### Unexpected Agent Behavior

**Symptom**: Agents are not behaving as expected

**Solution**: Enable debug logging to see detailed agent interactions:
```python
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("trust_dynamics")
logger.setLevel(logging.DEBUG)

# Create a file handler
handler = logging.FileHandler("debug_trust.log")
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

# Now run your simulation
model = create_model()
# ... rest of your code
```

## Getting Support

If you encounter problems not covered in this guide:

- Check the documentation in the `docs/` directory
- Look for similar issues in the `PROJECT_STATUS.md` file
- Examine the TRUST_DYNAMICS_ANALYSIS.md for known trust-related issues
- Contact the project maintainer at the email address listed in the README