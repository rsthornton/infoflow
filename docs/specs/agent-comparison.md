# Agent Types Comparison Table

## Citizen Agents vs. Social Media Agents

| Attribute | Citizen Agents | Corporate Media | Influencer Agents | Government Accounts |
|-----------|---------------|-----------------|-------------------|---------------------|
| **Primary Role** | Receive, process & share information | Create & broadcast content to wide audience | Create & share with dedicated followers | Official communications |
| **Scale Range** | | | | |
| Political Bias | N/A | -5 to +5 | -5 to +5 | -5 to +5 |
| Truth Seeking | -5 to +5 | N/A | N/A | N/A |
| Credibility | N/A | 0-10 | 0-10 | 0-10 |
| Authority | N/A | 0-10 (Medium-High) | 0-10 (Low-Medium) | 0-10 (High) |
| Truth Commitment | N/A | 0-10 (Medium-High) | 0-10 (Low-Medium) | 0-10 (Variable) |
| Confirmation Bias | 0-10 | N/A | N/A | N/A |
| Critical Thinking | 0-10 | N/A | N/A | N/A |
| Social Conformity | 0-10 | N/A | N/A | N/A |
| **Behaviors** | | | | |
| Receive Information | ✓ | ✗ | ✗ | ✗ |
| Process Information | ✓ | ✗ | ✗ | ✗ |
| Create Content | ✗ | ✓ | ✓ | ✓ |
| Share/Broadcast | ✓ (to connections) | ✓ (wide audience) | ✓ (followers) | ✓ (official channels) |
| Update Beliefs | ✓ | ✗ | ✗ | ✗ |
| Track Trust | ✓ | ✗ | ✗ | ✗ |
| Social Influence | ✓ | ✗ | ✗ | ✗ |
| | | | | |
| **Typical Values** | | | | |
| Publication Rate | Low (0.1-0.3) | Medium (0.4-0.7) | High (0.6-0.9) | Low (0.2-0.5) |
| Influence Reach | Low (connections only) | High (0.5-0.8) | Medium (0.3-0.6) | High (0.4-0.7) |
| Trust Impact | Low (per individual) | Medium | Medium-High | High |
| | | | | |
| **Unique Features** | | | | |
| | Confirmation bias | Institutional backing | Personal connection | Official authority |
| | Social influence | Formal verification | Higher engagement | Policy alignment |
| | Truth-seeking behavior | Wide distribution | Narrower targeting | Formal tone |
| | Network position | Resource-backed | Personality-driven | Regulatory power |
| **Mesa 3 Implementation** | | | | |
| | Managed via AgentSet | Optimized with create_agents() | Optimized with create_agents() | Optimized with create_agents() |
| | Vectorized operations | Property layer visualization | Follower tracking | Authority impact tracking |
| | Network-based influences | BatchRunner parameter testing | Engagement metrics | Policy preference modeling |

## Citizen Agent Subtypes

| Attribute | Truth Seeker | Neutral | Truth Avoider |
|-----------|--------------|---------|---------------|
| Truth Seeking | +2 to +5 | -1 to +1 | -2 to -5 |
| Confirmation Bias | Low (1-4) | Medium (4-7) | High (7-10) |
| Critical Thinking | High (7-10) | Medium (4-7) | Low (1-4) |
| Social Conformity | Low-Medium (2-5) | Medium (4-7) | High (7-10) |
| | | | |
| **Behaviors** | | | |
| Information Seeking | Active, diverse sources | Passive | Confirmation-seeking |
| Trust Updates | Evidence-based | Moderate updates | Alignment-based |
| Sharing Behavior | Selective, verified | Moderate | Frequent, aligned |
| Network Evolution | Diverse connections | Proximity-based | Echo chamber |
| | | | |
| **Mesa 3 Implementation** | | | |
| Creation Method | create_agents() with lambda parameter functions | create_agents() with lambda parameter functions | create_agents() with lambda parameter functions |
| Group Management | AgentSet filtering by truth_seeking value | AgentSet filtering by truth_seeking value | AgentSet filtering by truth_seeking value |
| Performance | Vectorized truth evaluation | Standard processing | Vectorized confirmation bias |
| Data Collection | Observable pattern for trust metrics | Standard DataCollector | Observable pattern for sharing metrics |

## Claim Properties

| Attribute | Description | Range | Example | Mesa 3 Implementation |
|-----------|-------------|-------|---------|---------------------|
| Truth Value | Degree of factual accuracy | 0-1 | 0.72 for "birds can fly" | Direct attribute |
| Verifiability | Ease of verification | 0-1 | 0.9 for "it rained yesterday" | Direct attribute |
| Uncertainty | Confidence interval width | 0-1 | 0.1 for scientific fact, 0.7 for policy prediction | Direct attribute |
| Content Type | Category of information | Categorical | News, Opinion, Analysis, etc. | Enumerated type |
| Emotional Impact | Emotional response strength | 0-1 | Higher values increase sharing probability | Direct attribute |
| Claim ID | Unique identifier | Integer | 1, 2, 3, etc. | Model-assigned ID |
| Spread Pattern | How claim propagates | Categorical | Viral, Linear, Cyclic | Tracked via property layer |
| Belief Distribution | Population belief distribution | Array | Array of belief values by agent | Visualized via property layer |

## Implementation Complexity

| Agent Type | Computational Complexity | Parameters Count | Behavioral Rules | Mesa 3 Implementation |
|-----------|--------------------------|------------------|------------------|------------------------|
| Citizen | Medium | 5-7 core parameters | 4-6 behavioral rules | Uses AgentSet, optimized with vectorized operations |
| Corporate Media | Low-Medium | 4-6 core parameters | 2-3 behavioral rules | Efficient with create_agents() method |
| Influencer | Low-Medium | 4-6 core parameters | 2-3 behavioral rules | Efficient with create_agents() method |
| Government | Low-Medium | 4-6 core parameters | 2-3 behavioral rules | Efficient with create_agents() method |
| Claim | Low | 3-5 attributes | N/A (passive object) | Can be tracked with property layers |
