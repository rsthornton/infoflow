# Mesa 3 Guide

This document provides a comprehensive guide to using Mesa 3 in the InfoFlow project, including quick reference information, migration notes, and troubleshooting tips.

## Installation Requirements

- **Python Version**: Mesa 3 requires Python 3.11 or higher
- **Installation Command**: `pip install "mesa[all]>=3.0.0"` (installs all optional dependencies)
- **Verify Installation**: Use `check_mesa.py` in project root to confirm proper functionality

## Key Mesa 3 Features in InfoFlow

- **AgentSet**: Powerful set-like class for organizing agents
- **Improved Scheduler**: Enhanced scheduling flexibility
- **Typing Support**: Better type annotations
- **Enhanced Data Collection**: More efficient data collection

## Using AgentSet

AgentSet is one of the most useful new features in Mesa 3:

```python
# Create a set of specific agent types
corporate_media_agents = AgentSet(model, [
    agent for agent in model.schedule.agents 
    if isinstance(agent, CorporateMediaAgent)
])

# Step only those agents
corporate_media_agents.step()

# Filter further if needed
trusted_corporate_media = corporate_media_agents.filter(
    lambda agent: agent.credibility > 7.0
)

# Selecting random subset
sample_agents = corporate_media_agents.random_select(5)
```

## Key Differences from Mesa 2

1. **Scheduler Changes**:
   - Mesa 3 uses `RandomActivation` by default
   - `SimultaneousActivation` has been removed
   - `RandomActivationByType` is reorganized

2. **API Changes**:
   - `DataCollector` takes model and agents in init
   - `Model` initialization requires scheduler
   - `Grid` has improved API and better typing

3. **Pattern Changes**:
   - Model initialization is more explicit
   - Better type checking throughout
   - `get_agent_vars_dataframe()` returns a differently structured DataFrame

## Troubleshooting Mesa 3 Issues

### Common Issues and Solutions

1. **ImportError: cannot import name 'SimultaneousActivation' from 'mesa'**
   - Mesa 3 removed SimultaneousActivation
   - Solution: Use StagedActivation instead

2. **TypeError: Model.__init__() missing required argument 'schedule'**
   - Mesa 3 requires explicit scheduler in model init
   - Solution: Add scheduler parameter to Model constructor

3. **AttributeError: 'Model' object has no attribute 'schedule_type'**
   - Mesa 3 removed schedule_type attribute
   - Solution: Create scheduler directly instead

4. **DataCollector initialization fails**
   - Mesa 3 changed DataCollector parameters
   - Solution: Update constructor call with model and agents parameters

5. **Error with model.step()**
   - Mesa 3 handles step differently
   - Solution: Ensure Model class uses proper step pattern

### Data Collection Changes

The most significant changes are in the data collection API:

```python
# Mesa 2
datacollector = DataCollector(
    model_reporters={"Avg": "average_metric"},
    agent_reporters={"Value": "value"}
)

# Mesa 3  
datacollector = DataCollector(
    model,  # Pass model instance directly
    model_reporters={"Avg": "average_metric"},
    agent_reporters={"Value": "value"}
)
```

### Pandas DataFrame Structure Changes

In Mesa 3, the agent DataFrame structure changed:

```python
# Mesa 2 
# Frame indexed by (iter, id)
frame.loc[(0, 1)]["Value"]  # Value of agent 1 at step 0

# Mesa 3
# Frame with MultiIndex of (AgentID, Step)
frame.xs(1, level="AgentID").loc[0]["Value"]  # Value of agent 1 at step 0
```

## Best Practices for Mesa 3 in InfoFlow

1. **Use AgentSet extensively**:
   - Create AgentSets for each agent type
   - Use filtering and selection for agent subgroups
   - Replace manual iteration with AgentSet methods

2. **Leverage Improved Typing**:
   - Add proper type annotations
   - Use mypy or Pyright to catch errors

3. **Data Collection**:
   - Use model variables more systematically
   - Create dedicated methods for data extraction
   - Be aware of DataFrame structure changes

4. **Reproducibility**:
   - Always set random seed in model
   - Use fixed seeds for reproducible tests

5. **Batch Runs**:
   - Mesa 3 has improved batch runner
   - Consider using it for parameter sweeps

## InfoFlow-Specific Mesa 3 Notes

In our codebase, we've adapted Mesa 3 usage in specific ways:

```python
# Creating model
model = InformationFlowModel(
    num_citizens=50,
    citizen_params={...},
    media_params={...},
    network_type="small_world",
    network_params={},
    seed=42
)

# Using agent sets
model.citizen_agents.step()
model.media_agents.step()

# Data collection
avg_trust = model.datacollector.get_model_vars_dataframe()["Average Trust in Government"]
```

## Migration Notes

When migrating existing Mesa 2 code to Mesa 3:

1. Check for deprecated SimultaneousActivation usage
2. Update Model initialization with scheduler
3. Update DataCollector initialization
4. Change DataFrame access patterns
5. Replace manual iteration with AgentSet where possible

For more detailed information, refer to the official Mesa documentation at https://mesa.readthedocs.io/en/stable/