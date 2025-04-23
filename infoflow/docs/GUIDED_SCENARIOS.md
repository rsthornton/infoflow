# Guided Scenarios

The InfoFlow social media simulation includes a set of carefully designed guided scenarios to demonstrate specific aspects of information dynamics in social media. These scenarios help users understand different phenomena related to information spread, belief formation, and trust dynamics.

## Available Scenarios

### 1. Viral Misinformation

**Context:** This scenario demonstrates how obviously false information can spread rapidly through social networks and social media platforms. By examining the emergence of echo chambers and viral content sharing patterns, you'll observe how cognitive biases enable misinformation to thrive despite being factually incorrect.

**Key Learning Objectives:**
- Observe how misinformation spreads despite being clearly false
- Identify the formation and reinforcement of echo chambers
- Understand how social media amplifiers accelerate the spread of false content
- Recognize how confirmation bias affects information processing

**Key Parameters:**
- High confirmation bias (6-9 range)
- Low critical thinking (2-5 range)
- Negative truth-seeking mean (-1.5)
- Strong trust in influencers (7.0)
- Low truth commitment from influencers (2.0)

### 2. Verifiable Fact Propagation

**Context:** This scenario explores how factual, easily verifiable information spreads through social networks. It demonstrates the dynamics of information dissemination when content has high accuracy and can be readily verified by multiple sources.

**Key Learning Objectives:**
- Compare the spread patterns of factual versus false information
- Observe how truth-seeking individuals influence network information quality
- Identify factors that promote the acceptance of accurate information
- Understand how trust in reliable sources affects information adoption

**Key Parameters:**
- Positive truth-seeking (mean 2.0)
- Moderate confirmation bias (3-6 range)
- Higher critical thinking (5-8 range)
- Balanced trust across sources
- High truth commitment from all sources (especially government at 8.0)

### 3. Pandemic Information Landscape

**Context:** This scenario models the complex information environment during a public health crisis like a pandemic. It showcases how uncertainty, evolving scientific understanding, and politicized viewpoints create a challenging landscape for accurate information dissemination.

**Key Learning Objectives:**
- Understand how pre-existing beliefs affect processing of new health information
- Observe how scientific uncertainty enables belief polarization
- Identify the role trusted authorities play in controversial situations
- Recognize how mixed messaging affects public trust and information acceptance

**Key Parameters:**
- High variance in truth-seeking (std 3.0)
- Mixed critical thinking (3-7 range)
- Medium-high confirmation bias (4-8 range)
- Scale-free network structure (creates hubs)
- More media sources (4 corporate, 8 influencers, 2 government)
- Longer simulation duration (75 steps)

## Running Guided Scenarios

1. Navigate to the "Guided Scenarios" page from the main navigation
2. Select a scenario that interests you
3. Review the scenario details, learning objectives, and parameter configurations
4. Click "Run Scenario" to start the simulation with the pre-configured parameters
5. After the simulation completes, you'll be redirected to the metrics dashboard
6. Use the observation guidance to explore different aspects of the simulation results

## Creating Custom Scenarios

You can create your own guided scenarios by adding JSON configuration files to the `infoflow/data/scenarios` directory. Each scenario file should include:

- `id`: Unique identifier for the scenario
- `name`: Display name for the scenario
- `description`: Brief explanation of what the scenario demonstrates
- `learning_objectives`: List of educational goals for the scenario
- `scenario_context`: Background story or setting for the scenario
- `observation_guidance`: Notes on what to look for in the results
- `simulation_parameters`: Dictionary of parameter values for the simulation

Your custom scenarios will automatically appear in the Guided Scenarios interface once added.

## Educational Value

Guided scenarios serve as interactive case studies for exploring social media dynamics. They demonstrate:

1. How different network structures affect information propagation
2. The impact of cognitive biases on information processing
3. How trust relationships evolve in response to information quality
4. The emergence of echo chambers and belief polarization
5. The role of influencers and authorities in shaping public belief

By comparing different scenarios, users can develop a deeper understanding of the complex factors that influence information dynamics in social media environments.