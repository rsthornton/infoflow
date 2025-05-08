Experimental Design

  1. Trust and Accuracy Experiments (Research Question 1)

  Design: 3×3×3 factorial design
  - Factor 1: Trust Level
    - Low trust in government (initial_trust_in_government = 1)
    - Medium trust in government (initial_trust_in_government = 5)
    - High trust in government (initial_trust_in_government = 8)
  - Factor 2: Content Accuracy
    - Low accuracy (truth_commitment_government = 1)
    - Medium accuracy (truth_commitment_government = 5)
    - High accuracy (truth_commitment_government = 10)
  - Factor 3: Replication
    - 3 random seeds per condition

  Total Runs: 27 simulations (9 conditions × 3 seeds)

  Held Constant:
  - Network type (small_world)
  - Network parameters (k=4, p=0.1)
  - Number of agents (100 citizens, 3 corporate media, 5 influencers, 1 government)
  - Cognitive parameters (confirmation_bias, critical_thinking, etc.)

  2. Network Structure Experiments (Research Question 2)

  Design: 3×3×3 factorial design
  - Factor 1: Network Type
    - Small-world networks (community-based)
    - Scale-free networks (hub-based)
    - Random networks (control condition)
  - Factor 2: Network Density
    - Low density
        - small_world_k = 2
      - scale_free_m = 1
      - random_p = 0.05
    - Medium density
        - small_world_k = 4
      - scale_free_m = 3
      - random_p = 0.1
    - High density
        - small_world_k = 8
      - scale_free_m = 5
      - random_p = 0.2
  - Factor 3: Replication
    - 3 random seeds per condition

  Total Runs: 27 simulations (9 conditions × 3 seeds)

  Held Constant:
  - Trust level (medium: initial_trust_in_government = 5)
  - Content accuracy (low: truth_commitment_government = 1)
  - Number of agents (100 citizens, 3 corporate media, 5 influencers, 1 government)
  - Cognitive parameters (confirmation_bias, critical_thinking, etc.)

  Simulation Procedure

  1. Each simulation ran for 74 time steps (shown to be sufficient for dynamics to stabilize)
  2. Media agents published content early in the simulation
  3. Citizens shared, evaluated, and responded to content
  4. Trust levels and truth assessments were tracked over time
  5. Final assessments were based on the average of the last 10 steps for stability

  Metrics and Measures

  Primary Dependent Variables:
  - Average truth assessment (citizens' beliefs about content accuracy)
  - Trust in government (citizens' trust in government sources)
  - Information spread patterns (how content propagated)

  Secondary Metrics:
  - Trust variance (polarization in trust)
  - Truth assessment variance (consensus vs. disagreement)
  - Trust evolution over time
  - Information flow patterns

  Analysis Approach

  1. Aggregation: Results across seeds were averaged to produce robust estimates
  2. Visualization: Heatmaps, bar charts, and line graphs to show relationships
  3. Comparison: Direct comparisons between conditions to test hypotheses
  4. Temporal Analysis: Examining how dynamics evolved over simulation time

  This systematic design provided a comprehensive approach to testing both how trust affects information ecosystem health and how network structure influences information spread, while controlling for
  confounding variables and ensuring reproducibility through multiple seeds.