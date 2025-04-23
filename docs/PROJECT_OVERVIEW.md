# InfoFlow Project Overview

## Introduction

InfoFlow is an agent-based model (ABM) that simulates how information flows through social networks and how agents evaluate the truthfulness of content. The simulation focuses on the dynamics of social media, modeling different types of sources (corporate, influencer, government) and how users interact with their content. The model helps researchers, educators, and policymakers explore how factors like political bias, source credibility, network structure, and individual cognitive differences affect information spread and belief formation.

## Project Purpose

The primary goals of the InfoFlow project are to:

1. **Simulate Social Media Dynamics**: Create a realistic model of how information travels through social networks
2. **Explore Trust Evolution**: Track how trust in different sources changes based on perceived accuracy
3. **Analyze Polarization**: Study how network structure and cognitive biases contribute to opinion polarization
4. **Test Interventions**: Evaluate potential interventions to improve information literacy and reduce misinformation

## Current Status: April 2025

The project has completed major development milestones with the following accomplishments:

### Core Simulation Features
- Implemented sophisticated truth assessment update mechanics for social media users
- Created specialized media agent types (corporate, influencer, government) with distinctive behaviors
- Developed realistic cognitive models for confirmation bias, critical thinking, and social conformity
- Implemented multiple network topologies to simulate different social media environments

### Network Visualization Enhancements
- Created interactive network visualization with multiple layouts
- Implemented content flow tracking showing how information spreads through the network
- Added color coding for content accuracy (green/yellow/red for true/fuzzy/false)
- Created distinctive line styles for different media sources (solid/dashed/dotted)
- Added time-step and hop-by-hop visualization modes
- Implemented timeline slider for step-by-step content propagation tracking

### Data Analysis Capabilities
- Added detailed data collection tracking truth assessments, trust dynamics, and polarization metrics
- Implemented comprehensive export system (JSON, chart images, interactive HTML)
- Created agent tracking for individual-level analysis
- Added visualization of trust and belief evolution over time

### User Interface Improvements
- Developed intuitive parameter organization with presets
- Created tabbed interface separating network visualization from charts
- Added content legend showing source types and accuracy indicators
- Implemented tooltips throughout the interface for better usability

## Key Concepts

### Truth Assessment vs. Belief

A critical insight from Stage 2 was properly distinguishing between related but distinct concepts:

| Concept | Scale | Description |
|---------|-------|-------------|
| **Truth Assessment** | 0-1 | Agent's evaluation of how true a claim is (0.5 is neutral) |
| **Political Bias** | -5 to +5 | How information is framed (anti-Trump to pro-Trump) |
| **Accuracy** | 0-1 | The objective truthfulness of content |

This distinction creates a more realistic model following the specification's intent and allows for more nuanced interactions between objective truth and subjective assessments. We've updated all terminology to use "truth assessment" for clarity.

### Agent Types and Characteristics

#### Citizen Agents
Citizens are the primary consumers of content who make truth assessments and share information:

| Attribute | Scale | Description |
|-----------|-------|-------------|
| Truth Seeking | -5 to 5 | Motivation to find accurate information (negative values avoid challenging information) |
| Confirmation Bias | 0-10 | Tendency to favor content aligned with existing views |
| Critical Thinking | 0-10 | Ability to evaluate source credibility |
| Social Conformity | 0-10 | Tendency to align truth assessments with social connections |
| Influence | 0-10 | Impact on connected users when sharing content |

#### Media Agents

The simulation includes three specialized types of media agents:

| Media Type | Key Characteristics | Real-world Analog |
|------------|---------------------|-------------------|
| **Corporate Media** | Higher authority & credibility, broad untargeted reach | News organizations on social media |
| **Influencers** | Higher engagement, follower management, more frequent content | Social media personalities, YouTubers |
| **Government** | Highest authority, variable truth commitment | Official government accounts |

All media agents have parameters for:
- Political bias (framing bias)
- Truth commitment (fact-checking threshold)
- Publication rate (content creation frequency)
- Influence reach (audience size)

### Network Dynamics

The model supports multiple network structures to simulate different social media environments:

| Network Type | Properties | Real-world Analog |
|--------------|------------|-------------------|
| **Small World** | Community structure with some long-range connections | Facebook friend networks |
| **Scale Free** | Few highly-connected hubs, many nodes with few connections | Twitter follower structure |
| **Random** | Random connections without community structure | Control case for comparison |

## Implementation Details

### Simulation Workflow

The model follows a specific workflow during each simulation step:

1. **Content Creation**: Media agents create and publish content based on their parameters
   - Content has attributes for accuracy, bias, credibility, and authority
   - Publication depends on individual media agent publication rates

2. **Social Influence**: Citizens update truth assessments based on their social connections
   - Higher social conformity leads to stronger network influence
   - Influence is weighted by neighbor influence values

3. **Information Seeking**: Truth-seeking citizens actively look for information
   - Citizens with positive truth-seeking values proactively seek content
   - Source selection is influenced by trust levels

4. **Content Sharing**: Citizens decide whether to share content with their neighbors
   - Sharing probability depends on confidence and alignment
   - Content can be modified during sharing (framing bias adjustment)

5. **Trust Updates**: Trust in sources is updated based on perceived accuracy
   - Critical thinking affects the magnitude of trust adjustments
   - Trust evolves differently for different cognitive profiles

### Data Collection

The simulation collects extensive data for analysis:

#### Model-Level Metrics
- Average truth assessment (population belief)
- Truth assessment variance (polarization)
- Trust levels for different source types
- Trust variance (trust polarization)
- Social network metrics (clustering, etc.)

#### Agent-Level Metrics
- Individual truth assessments
- Personal trust in each source type
- Content consumption patterns
- Sharing behavior

### Visualization Components

The web interface provides multiple visualization types:

- **Time Series Charts**: Track metrics over simulation time
- **Distribution Plots**: Show how values are distributed across the population
- **Network Visualization**: Interactive view of agent connections and states
- **Correlation Plots**: Explore relationships between agent attributes and outcomes

## Next Steps (Stage 3)

The upcoming Stage 3 development will focus on:

### Enhanced Web Interface
- Implement more sophisticated interactive visualizations
- Add comprehensive dashboards for detailed analysis
- Create scenario comparison tools
- Improve user experience with better parameter organization

### Advanced Model Features
- Add explicit Claim objects with truth values
- Implement dynamic network evolution (friendship formation/dissolution)
- Develop more sophisticated truth-seeking strategies
- Add content virality and engagement mechanics

### Performance Optimization
- Profile and optimize for larger simulations (1000+ agents)
- Implement parallel processing for parameter sweeps
- Optimize visualization rendering for complex networks
- Add caching for frequently accessed metrics

## Usage Examples

### Basic Model Creation

```python
from infoflow.core.model import create_model

# Create model with default parameters
model = create_model()

# Run simulation for 10 steps
for _ in range(10):
    model.step()

# Access data
df = model.datacollector.get_model_vars_dataframe()
```

### Custom Parameter Configuration

```python
# Create a model with specific parameters
model = create_model(
    # Network configuration
    network_type="scale_free",
    scale_free_m=4,
    
    # Agent population
    num_citizens=100,
    num_corporate_media=5,
    num_influencers=10,
    num_government=2,
    
    # Cognitive parameters
    truth_seeking_mean=2.0,
    confirmation_bias_min=3,
    confirmation_bias_max=8,
    critical_thinking_min=4,
    critical_thinking_max=9,
    
    # Media parameters
    corporate_bias_min=-3,
    corporate_bias_max=3,
    truth_commitment_corporate=7.0
)
```

### Web Application

The interactive web interface provides a user-friendly way to run simulations:

```bash
python run_server.py
```

Visit http://127.0.0.1:5001 in your browser to access the interface.

## Related Documentation

For more information about specific aspects of the project, see:
- [User Guide](usage/user_guide.md) - How to use the simulation and interpret results
- [Code Structure](CODE_STRUCTURE.md) - Detailed code organization
- [Trust Dynamics Analysis](reports/TRUST_DYNAMICS_ANALYSIS.md) - Analysis of trust evolution
- [System Architecture](architecture/system_architecture.md) - Technical architecture overview