# InfoFlow API Reference

This document provides detailed information about the core classes and functions in the InfoFlow simulation system. Use this reference to understand the available APIs when extending or integrating the system.

## Table of Contents

1. [Core Model](#core-model)
2. [Agents](#agents)
   - [Base Agents](#base-agents)
   - [Media Agents](#media-agents)
3. [Networks](#networks)
4. [Data Collection](#data-collection)
5. [Visualization](#visualization)
6. [Utilities](#utilities)
7. [Web Interface](#web-interface)

---

## Core Model

### InformationFlowModel

```python
class InformationFlowModel(mesa.Model)
```

The central model class that coordinates the simulation.

#### Constructor

```python
def __init__(
    self,
    num_citizens: int = 50,
    num_corporate_media: int = 3,
    num_influencers: int = 5,
    num_government: int = 1,
    citizen_params: Optional[Dict] = None,
    media_params: Optional[Dict] = None,
    network_type: str = "small_world",
    network_params: Optional[Dict] = None,
    seed: Optional[int] = None
)
```

**Parameters:**
- `num_citizens`: Number of citizen agents to create
- `num_corporate_media`: Number of corporate media agents
- `num_influencers`: Number of influencer agents
- `num_government`: Number of government media agents
- `citizen_params`: Dictionary of parameters for citizen agents
- `media_params`: Dictionary of parameters for media agents
- `network_type`: Type of network to create ("small_world", "scale_free", "random")
- `network_params`: Parameters for network creation
- `seed`: Random seed for reproducibility

#### Key Methods

```python
def step(self)
```
Execute one step of the model, including all agents' actions.

```python
def setup_connections(self)
```
Set up all network connections after agents are created.

```python
def _create_network(self) -> nx.Graph
```
Create a network of the specified type.

```python
def _create_citizen_agents(self)
```
Create and place citizen agents in the network.

```python
def _create_media_agents(self)
```
Create media agents of different types.

```python
def _setup_data_collection(self)
```
Set up data collection for the model.

```python
def _get_parameters_dict(self) -> Dict
```
Get a dictionary of all model parameters for stats collection.

```python
def _record_stats(self)
```
Record detailed statistics for the current step.

### create_model

```python
def create_model(**kwargs) -> InformationFlowModel
```

Creates and initializes a model with the given parameters.

**Parameters:**
- All parameters accepted by `InformationFlowModel.__init__`
- Additional parameters for fine-grained control (see source for full list)

**Returns:**
- A fully initialized `InformationFlowModel` instance

---

## Agents

### Base Agents

#### BaseAgent

```python
class BaseAgent(mesa.Agent)
```

Base class for all agent types in the simulation.

**Methods:**
```python
def step(self)
```
Base step method to be implemented by subclasses.

#### CitizenAgent

```python
class CitizenAgent(BaseAgent)
```

Citizens who consume, process, and share information from various sources.

**Constructor:**
```python
def __init__(
    self,
    model: mesa.Model,
    initial_truth_assessment: float = 0.5,
    confidence: float = 5.0,
    truth_seeking: float = 0.0,
    confirmation_bias: float = 5.0,
    critical_thinking: float = 5.0,
    influence: float = 5.0,
    social_conformity: float = 5.0
)
```

**Parameters:**
- `model`: Model instance the agent belongs to
- `initial_truth_assessment`: Starting truth assessment value (0-1 scale)
- `confidence`: Strength of truth assessment (0-10 scale)
- `truth_seeking`: Attitude toward truth (-5 to 5 scale)
- `confirmation_bias`: Tendency to favor aligned content (0-10 scale)
- `critical_thinking`: Ability to evaluate source credibility (0-10 scale)
- `influence`: Impact on connected citizens (0-10 scale)
- `social_conformity`: Tendency to align with social circle (0-10 scale)

**Methods:**
```python
def receive_information(self, content: Dict[str, Any], source: BaseAgent) -> bool
```
Process incoming information and decides whether to accept it.

```python
def update_trust(self, source_type: str, perceived_accuracy: float)
```
Update trust in a source type based on perceived accuracy.

```python
def share_information(self) -> Optional[Dict[str, Any]]
```
Decide whether to share content and which content to share.

```python
def be_influenced_by_network(self)
```
Update truth assessments based on connections in the network.

```python
def seek_information(self)
```
Actively seek new information (for truth-seeking agents).

```python
def step(self)
```
Execute one step of the citizen agent.

#### SocialMediaAgent

```python
class SocialMediaAgent(BaseAgent)
```

Base class for all social media agent types.

**Constructor:**
```python
def __init__(
    self,
    model: mesa.Model,
    political_bias: float = 0.0,
    credibility: float = 5.0,
    authority: float = 5.0,
    truth_commitment: float = 5.0,
    influence_reach: float = 0.5,
    publication_rate: float = 0.5
)
```

**Parameters:**
- `model`: Model instance the agent belongs to
- `political_bias`: Political leaning (-5 to 5 scale)
- `credibility`: Perceived reliability (0-10 scale)
- `authority`: Institutional influence (0-10 scale)
- `truth_commitment`: Fact-checking threshold (0-10 scale)
- `influence_reach`: Proportion of citizens reached (0-1 scale)
- `publication_rate`: Frequency of content creation (0-1 scale)

**Methods:**
```python
def create_content(self) -> Dict[str, float]
```
Create content based on agent properties.

```python
def publish_content(self) -> Optional[Dict[str, float]]
```
Check if content should be published this step based on publication_rate.

```python
def broadcast_content(self, content: Dict[str, float]) -> List[CitizenAgent]
```
Distribute content to appropriate citizen agents.

```python
def step(self)
```
Execute one step of the social media agent.

### Media Agents

#### CorporateMediaAgent

```python
class CorporateMediaAgent(SocialMediaAgent)
```

Corporate media organizations with balanced credibility.

**Constructor:**
```python
def __init__(
    self,
    model: mesa.Model,
    political_bias: float = 0.0,
    credibility: float = 7.0,
    authority: float = 6.0,
    truth_commitment: float = 7.0,
    influence_reach: float = 0.7,
    publication_rate: float = 0.8
)
```

**Methods:**
```python
def create_content(self) -> Dict[str, Any]
```
Create content with balanced attributes.

```python
def broadcast_content(self, content: Dict[str, Any]) -> List[CitizenAgent]
```
Distribute content to a wide audience.

#### InfluencerAgent

```python
class InfluencerAgent(SocialMediaAgent)
```

Individual social media influencers with followers.

**Constructor:**
```python
def __init__(
    self,
    model: mesa.Model,
    political_bias: float = 0.0,
    credibility: float = 4.0,
    authority: float = 3.0,
    truth_commitment: float = 4.0,
    influence_reach: float = 0.5,
    publication_rate: float = 0.9,
    engagement_factor: float = 1.5
)
```

**Additional Attributes:**
- `followers`: List of citizen agents following this influencer
- `engagement_factor`: Boost to content acceptance probability

**Methods:**
```python
def add_follower(self, citizen: CitizenAgent)
```
Add a citizen as a follower.

```python
def create_content(self) -> Dict[str, Any]
```
Create content with high engagement but variable accuracy.

```python
def broadcast_content(self, content: Dict[str, Any]) -> List[CitizenAgent]
```
Distribute content to followers.

#### GovernmentMediaAgent

```python
class GovernmentMediaAgent(SocialMediaAgent)
```

Official government media channels with high authority.

**Constructor:**
```python
def __init__(
    self,
    model: mesa.Model,
    political_bias: float = 0.0,
    credibility: float = 6.0,
    authority: float = 9.0,
    truth_commitment: float = 5.0,
    influence_reach: float = 0.6,
    publication_rate: float = 0.3
)
```

**Methods:**
```python
def create_content(self) -> Dict[str, Any]
```
Create content with higher authority impact.

```python
def broadcast_content(self, content: Dict[str, Any]) -> List[CitizenAgent]
```
Distribute content with high authority impact.

---

## Networks

### Core Functions

```python
def create_network(
    network_type: str,
    num_nodes: int,
    params: Dict[str, Any],
    seed: Optional[int] = None
) -> nx.Graph
```

Create a network of the specified type.

**Parameters:**
- `network_type`: Type of network to create ("small_world", "scale_free", "random")
- `num_nodes`: Number of nodes in the network
- `params`: Parameters for network creation
- `seed`: Random seed for reproducibility

**Returns:**
- A networkx graph object

### Network Type Functions

```python
def create_small_world_network(
    num_nodes: int,
    k: int = 4,
    p: float = 0.1,
    seed: Optional[int] = None
) -> nx.Graph
```

Create a small-world network using the Watts-Strogatz model.

```python
def create_scale_free_network(
    num_nodes: int,
    m: int = 3,
    seed: Optional[int] = None
) -> nx.Graph
```

Create a scale-free network using the Barabasi-Albert model.

```python
def create_random_network(
    num_nodes: int,
    p: float = 0.1,
    seed: Optional[int] = None
) -> nx.Graph
```

Create a random network using the Erdos-Renyi model.

---

## Data Collection

### DataCollector

The model uses Mesa's built-in `DataCollector` class:

```python
datacollector = mesa.DataCollector(
    model_reporters={
        # Model-level metrics
        "Average Truth Assessment": lambda m: np.mean([a.truth_assessment for a in m.citizens]),
        # Other metrics...
    },
    agent_reporters={
        # Agent-level metrics
        "Truth Assessment": lambda a: getattr(a, "truth_assessment", None),
        # Other metrics...
    }
)
```

**Usage:**
```python
# Collect data
datacollector.collect(model)

# Get model-level data
model_data = datacollector.get_model_vars_dataframe()

# Get agent-level data
agent_data = datacollector.get_agent_vars_dataframe()
```

### StatsCollector

Custom statistics collector in `infoflow/utils/simple_stats.py`:

```python
class StatsCollector
```

**Key Methods:**
```python
def start_run(self, parameters: Dict)
```
Initialize a new simulation run with the given parameters.

```python
def record_step(self, step: int, metrics: Dict)
```
Record metrics for a simulation step.

```python
def finish_run(self)
```
Finalize the current simulation run.

```python
def name_run(self, name: str)
```
Add a human-readable name to a simulation run.

**Static Methods:**
```python
@staticmethod
def get_recent_runs(limit: int = 20) -> List[Dict]
```
Get a list of recent simulation runs.

```python
@staticmethod
def get_run_data(run_id: str) -> Dict
```
Get complete data for a specific simulation run.

---

## Visualization

### Core Plotting Functions

From `infoflow/data/visualization.py`:

```python
def plot_truth_assessment_distribution(
    truth_assessments: List[float],
    title: str = "Truth Assessment Distribution"
) -> plt.Figure
```

Plot a histogram of truth assessments.

```python
def plot_trust_levels(data: Dict[str, List[float]]) -> plt.Figure
```

Plot average trust levels for different source types over time.

```python
def plot_truth_assessment_evolution(data: Dict[str, List[float]]) -> plt.Figure
```

Plot the evolution of truth assessment metrics over time.

```python
def create_network_visualization(
    model,
    node_color_attribute: str = 'truth_assessment'
) -> plt.Figure
```

Create a visualization of the agent network.

---

## Utilities

### Helper Functions

From `infoflow/utils/helpers.py`:

```python
def calculate_variance(values: List[float]) -> float
```

Calculate variance of a list of values.

```python
def generate_unique_id(prefix: str = "sim") -> str
```

Generate a unique identifier with timestamp.

### Simple Stats

From `infoflow/utils/simple_stats.py`:

```python
def initialize_database()
```

Initialize the SQLite database for storing simulation statistics.

```python
def save_run_parameters(run_id: str, parameters: Dict)
```

Save simulation parameters to the database.

```python
def save_run_data(run_id: str, data: Dict)
```

Save simulation data to the database.

---

## Web Interface

### Flask Routes

From `infoflow/web/routes.py`:

```python
@bp.route('/')
def index()
```
Render the main page.

```python
@bp.route('/simulation')
def simulation()
```
Render the simulation page.

```python
@bp.route('/simulations')
def simulations()
```
Render the simulation history page.

### API Endpoints

```python
@bp.route('/api/run-simulation', methods=['POST'])
def run_simulation()
```
Run a simulation with the provided parameters.

```python
@bp.route('/api/simulation-runs', methods=['GET'])
def get_simulation_runs()
```
Get a list of recent simulation runs.

```python
@bp.route('/api/simulation-data/<run_id>', methods=['GET'])
def get_simulation_data(run_id)
```
Get complete data for a simulation run.

```python
@bp.route('/api/name-simulation', methods=['POST'])
def name_simulation()
```
Add a name to a simulation run.