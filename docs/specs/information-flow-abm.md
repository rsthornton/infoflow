# Information Flow in Social Networks: Agent-Based Model Specification

This document provides a comprehensive specification for an agent-based model (ABM) simulating information flow in social networks with a focus on how truth propagates through different agent types.

## 1. Core Concepts

### 1.1 Truth and Verifiability of Claims

#### 1.1.1 Claim-Specific Truth Values
- The model centers on **specific claims** being shared through the network
- Each claim has an associated "truth value" on a spectrum from 0 to 1:
  - 0: "Completely false"
  - 1: "Completely true"
  - Values between: Partially true claims (e.g., 0.72 for "birds can fly")
- This approach uses fuzzy logic to represent the spectrum of truth in real-world claims

#### 1.1.2 Verifiability Dimension
- Claims also have a "verifiability" attribute representing how easily they can be verified:
  - High (0.8-1.0): Easily verified with evidence (e.g., "it rained yesterday")
  - Medium (0.4-0.7): Requires expertise to verify (e.g., "this medication is effective")
  - Low (0-0.3): Difficult or impossible to verify (e.g., "this policy is the most fair")

#### 1.1.3 Uncertainty Parameter
- Claims have an "uncertainty" attribute representing epistemic limitations:
  - The confidence interval around the truth value
  - Higher uncertainty makes the claim more susceptible to interpretation
  - Uncertainty can be intrinsic to the claim or due to limited evidence

#### 1.1.4 Information Quality
- Information quality is measured by how closely an agent's belief about a claim aligns with its actual truth value
- Agents assess this alignment through their own perceptual filters (confirmation bias, trust in sources)

### 1.2 Beliefs
- All agents hold beliefs ranging from 0 to 1 (where 0.5 is neutral)
- Belief strength (confidence) ranges from 0-10

### 1.3 Network Structure
- Agents exist in a social network with connections between them
- Information flows along network connections
- Network topology significantly impacts information propagation

## 2. Agent Types

### 2.1 Base Agent Properties
All agents share these base properties:
- `unique_id`: Unique identifier
- `model`: Reference to the model
- `step()`: Standard action method

### 2.2 Citizen Agents

#### 2.2.1 Properties
- `belief`: 0-1 scale representing belief about current topic (0.5 is neutral)
- `confidence`: 0-10 scale of belief strength
- `truth_seeking`: -5 to 5 scale
  - Positive: Actively seeks truth
  - Zero: Neutral approach
  - Negative: Avoids truth/prefers comfortable narratives
- `confirmation_bias`: 0-10 scale (tendency to favor aligned content)
- `critical_thinking`: 0-10 scale (ability to evaluate source credibility)
- `influence`: 0-10 scale (impact on connected citizens)
- `connections`: List of connected citizens
- `social_conformity`: 0-10 scale (tendency to align with social circle)
- `trust_levels`: Dictionary tracking trust in different source types

#### 2.2.2 Behaviors
- **Receive Information**
  ```
  Input: Content object, Source agent
  Process:
    1. Extract content properties (accuracy, bias, source_type)
    2. Apply source trust filter
    3. Calculate confirmation bias effect based on belief alignment
    4. Apply critical thinking to evaluate accuracy
    5. Update belief if content is accepted
    6. Adjust confidence based on belief change
    7. Update trust in source
  Output: Updated belief and trust states
  ```

- **Share Information**
  ```
  Process:
    1. Select content to share (preferring high alignment)
    2. Determine sharing probability based on confidence
    3. Apply personal framing based on belief
    4. Reduce accuracy slightly with each share
    5. Share with connected agents
  ```

- **Social Influence**
  ```
  Process:
    1. Collect beliefs from connections
    2. Weight by connection influence
    3. Calculate weighted average belief
    4. Update own belief based on social_conformity
  ```

- **Seek Information** (for truth-seeking citizens)
  ```
  Process:
    1. Select information sources based on truth_seeking orientation
    2. Truth seekers (+): seek diverse, credible sources
    3. Truth avoiders (-): seek confirming sources
    4. Request content directly from selected sources
  ```

### 2.3 Social Media Agents

#### 2.3.1 Common Properties
- `political_bias`: -5 to 5 scale (anti-Trump to pro-Trump)
- `credibility`: 0-10 scale (perceived reliability)
- `authority`: 0-10 scale (institutional influence)
- `truth_commitment`: 0-10 scale (fact-checking threshold)
- `influence_reach`: 0-1 scale (proportion of citizens reached)
- `publication_rate`: 0-1 scale (frequency of content creation)

#### 2.3.2 Common Behaviors
- **Create Content**
  ```
  Process:
    1. Generate base accuracy based on truth_commitment
    2. Apply political bias to content framing
    3. Include source metadata (authority, credibility)
  Output: Content object with properties:
    - accuracy: How closely content reflects ground truth (0-1)
    - framing_bias: Political framing (-1 to 1)
    - source_authority: Authority level (0-1)
    - source_credibility: Credibility level (0-1)
    - source_type: Agent class name
  ```

- **Publish Content**
  ```
  Process:
    1. Check if content should be published this step (publication_rate)
    2. If yes, create and broadcast content
  ```

- **Broadcast Content**
  ```
  Process:
    1. Determine reach based on agent type and properties
    2. Distribute content to appropriate citizen agents
  ```

#### 2.3.3 Agent-Specific Properties

##### Corporate Media Agents
- Higher authority and credibility on average
- Moderate publication rate
- Wide but less targeted distribution

##### Influencer Agents
- Maintains follower network
- Higher publication rate
- Higher engagement with audience
- Lower truth_commitment on average

##### Government Media Accounts
- Highest authority on average
- Lower publication rate
- Stronger authority impact on citizens
- Political bias aligned with current administration

## 3. Interaction Protocol

### 3.1 Content Object Structure
```json
{
  "accuracy": 0.7,          // 0-1 scale, how factual is the content
  "framing_bias": 0.2,      // -1 to 1 scale, political framing
  "source_authority": 0.8,  // 0-1 scale, perceived authority
  "source_credibility": 0.6, // 0-1 scale, perceived credibility  
  "source_type": "CorporateMediaAgent", // Type of the source
  "engagement_factor": 1.2,  // Optional: engagement multiplier
  "authority_factor": 1.5    // Optional: authority multiplier
}
```

### 3.2 Information Flow
1. Social Media Agents create content with properties based on their attributes
2. Content is broadcast to Citizen Agents based on reach and network
3. Citizens process content based on their attributes:
   - Apply confirmation bias filter
   - Apply source trust filter
   - Update beliefs if content passes filters
4. Citizens share content with their connections:
   - Apply personal framing
   - Reduce accuracy slightly
5. Citizens influence each other directly through social network
6. Truth-seeking citizens actively seek additional information

### 3.3 Trust Dynamics
- Citizens track trust separately for each source type
- Trust increases when perceived information matches ground truth
- Trust decreases when information seems inaccurate
- Trust levels affect future information acceptance
- Critical thinkers adjust trust more based on perceived accuracy

## 4. Implementation Guidelines

### 4.1 Model Initialization
1. Set truth value, verifiability, and uncertainty for claims in the simulation
2. Create Citizen Agents with distribution of attributes using `create_agents()` method
3. Create Social Media Agents with varied properties
4. Initialize network connections between agents
5. Set up property layers for tracking information spread

### 4.2 Simulation Steps
For each step:
1. Social Media Agents create and publish content
2. Citizen Agents receive and process information
3. Citizen Agents update trust levels for sources
4. Citizen Agents share information with connections
5. Citizen Agents are influenced by social network
6. Truth-seeking Citizen Agents seek additional information
7. Update property layers to visualize information spread
8. Collect data using Mesa's DataCollector

### 4.3 Metrics
Track these metrics to analyze simulation:
- Average belief across all citizens
- Belief distribution (histogram)
- Trust levels for different source types
- Information accuracy across the network
- Polarization measure (belief variance)
- Content sharing patterns

## 5. Incremental Implementation Plan

### Phase 1: Basic Model
- Implement Citizen Agents with basic belief updates
- Implement simple network structure using Mesa 3's NetworkGrid
- Implement one type of information source
- Set up DataCollector for basic metrics
- Use NumPy's random generator (`self.random.integers()`) instead of older methods

### Phase 2: Enhanced Agent Types
- Add truth-seeking attribute to citizens
- Implement all three Social Media Agent types
- Enhance content creation and distribution
- Use Mesa 3's `create_agents()` method for efficient agent creation
- Implement `AgentSet` for managing groups of similar agents

### Phase 3: Complex Dynamics
- Implement trust tracking for different sources
- Add confirmation bias and critical thinking
- Implement sharing behavior with personal framing
- Add property layers for visualizing information spread
- Update visualization to use Mesa 3's improved modules

### Phase 4: Advanced Features
- Add dynamic network evolution
- Implement competing claims with different truth values, verifiability and uncertainty
- Add strategic behavior to government and media agents
- Implement batch simulations for parameter exploration
- Use Mesa 3's Observable pattern for dynamic data tracking

## 6. Sample Code Structures

### 6.1 Agent Class Structure
```python
class Citizen(mesa.Agent):
    def __init__(self, unique_id, model, initial_belief, truth_seeking,
                 confirmation_bias, critical_thinking, social_conformity, influence):
        # Initialize properties
        
    def receive_information(self, content, source):
        # Process incoming information
        
    def update_trust(self, source_type, perceived_accuracy):
        # Update trust in sources
        
    def share_information(self):
        # Share content with connections
        
    def be_influenced_by_network(self):
        # Update beliefs based on connections
        
    def seek_information(self):
        # Actively seek new information
        
    def step(self):
        # Perform agent actions each step

class InformationFlowModel(mesa.Model):
    def __init__(self, N, network_type, citizen_params, media_params, seed=None):
        super().__init__()
        self.num_agents = N
        self.schedule = mesa.time.RandomActivation(self)
        self.random = np.random.default_rng(seed)  # Mesa 3's random generator
        
        # Create network
        G = self._initialize_network(network_type)
        self.grid = mesa.space.NetworkGrid(G)
        
        # Create property layer for information spread
        self.grid.property_layers["info_spread"] = np.zeros(N)
        
        # Create citizen agents efficiently using create_agents
        self.create_agents(
            Citizen, 
            self.num_agents, 
            initial_belief=lambda: self.random.random(),
            truth_seeking=lambda: citizen_params["truth_seeking"] + self.random.integers(-2, 3),
            confirmation_bias=lambda: self.random.integers(3, 8),
            critical_thinking=lambda: self.random.integers(3, 8),
            social_conformity=lambda: self.random.integers(3, 8),
            influence=lambda: self.random.integers(1, 10)
        )
        
        # Create media agents
        # ...
        
        # Group agents by type using AgentSet
        self.citizens = mesa.AgentSet(self, {
            agent.unique_id: agent for agent in self.schedule.agents 
            if isinstance(agent, Citizen)
        })
        
        self.media_agents = mesa.AgentSet(self, {
            agent.unique_id: agent for agent in self.schedule.agents 
            if isinstance(agent, MediaAgent)
        })
        
        # Set up data collection
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Average Belief": lambda m: m.citizens.aggregate("belief", np.mean),
                "Belief Variance": lambda m: np.var([a.belief for a in m.citizens]),
                "Trust in Media": lambda m: m.citizens.aggregate(
                    lambda a: a.trust["CorporateMediaAgent"], np.mean)
            },
            agent_reporters={
                "Belief": "belief",
                "Trust_Corporate": lambda a: getattr(a, "trust", {}).get("CorporateMediaAgent", None)
            }
        )
```

### 6.2 Content Structure
```python
def create_content(self, claim):
    """Create content about a specific claim."""
    # Base accuracy tied to truth commitment and claim verifiability
    base_accuracy = (self.truth_commitment / 10.0) * claim.verifiability
    
    # Apply randomness based on claim uncertainty
    accuracy_noise = self.random.uniform(-claim.uncertainty, claim.uncertainty)
    actual_accuracy = min(1.0, max(0.0, base_accuracy + accuracy_noise))
    
    # Political bias affects framing
    framing_bias = self.political_bias / 5.0
    
    return {
        "claim": claim,
        "accuracy": actual_accuracy,
        "framing_bias": framing_bias,
        "source_authority": self.authority / 10.0,
        "source_credibility": self.credibility / 10.0,
        "source_type": self.__class__.__name__
    }

class Claim:
    """Represents a claim being shared in the network."""
    
    def __init__(self, content, truth_value, verifiability, uncertainty):
        self.content = content
        self.truth_value = truth_value  # 0-1 scale
        self.verifiability = verifiability  # 0-1 scale
        self.uncertainty = uncertainty  # 0-1 scale
```

## 7. Advanced Considerations

### 7.1 Media Content Types
Media agents could produce different types of content:
- News (higher accuracy expectations)
- Opinion (more explicit bias)
- Analysis (more complex, requiring higher critical thinking)
- Entertainment (lower accuracy expectations)

### 7.2 Network Evolution
- Citizens could adjust connections based on belief alignment
- Trust in sources could affect likelihood of exposure
- Filter bubbles could emerge from agent behavior
- Use Mesa 3's dynamic network capabilities to modify links during simulation

### 7.3 Multiple Claims
- Track separate beliefs for different claims
- Allow correlations between claim beliefs
- Model how credibility transfers across claims
- Use property layers to visualize belief distribution for each claim

### 7.4 Strategic Behavior
- Government agents could adjust messaging based on public opinion
- Media agents could optimize for engagement vs. accuracy
- Citizens could develop more sophisticated information-seeking strategies
- Implement Mesa 3 Observables to dynamically track strategic shifts

### 7.5 Performance Optimization
- Use AgentSet for efficient agent group operations
- Leverage Mesa 3's optimized data structures
- Implement parallel batch runs for parameter sweeps
- Use numpy vectorized operations when processing large agent groups

## 8. Parameter Sensitivity

Key parameters to test:
- Truth-seeking distribution
- Network structure
- Media agent political bias
- Trust update rates
- Initial belief distribution
- Claim properties (truth value, verifiability, uncertainty)

Explore how these parameters affect:
- Speed of belief convergence
- Final belief distribution
- Trust dynamics
- Polarization metrics
- Information accuracy

### 8.1 Using Mesa 3's BatchRunner

```python
from mesa.batchrunner import BatchRunner

# Define parameters to vary
parameters = {
    "N": [50, 100, 200],
    "network_type": ["small_world", "scale_free", "random"],
    "citizen_truth_seeking": [-5, 0, 5],
    "media_bias": [-5, 0, 5],
    "claim_verifiability": [0.2, 0.5, 0.8],
    "claim_uncertainty": [0.1, 0.3, 0.5]
}

# Define what to measure
model_reporters = {
    "Average Belief": lambda m: m.average_belief(),
    "Belief Variance": lambda m: m.belief_variance(),
    "Truth Alignment": lambda m: m.truth_alignment()
}

# Create a batch runner
batch_run = BatchRunner(
    InformationFlowModel,
    parameters,
    model_reporters=model_reporters,
    iterations=5,  # Run each parameter combination 5 times
    max_steps=50   # Run each model for 50 steps
)

# Run the experiments
batch_run.run_all()

# Get and analyze the data
run_data = batch_run.get_model_vars_dataframe()
```

## 9. Conclusion

This specification provides a foundation for building an agent-based model of information flow in social networks. By implementing this model incrementally, you can create a rigorous simulation that captures the complex dynamics of truth, belief, and media influence in social systems.
