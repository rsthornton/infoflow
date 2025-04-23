"""
Core model for the InfoFlow simulation.

This module defines the central model class that coordinates agent interactions
and network structure for the information flow simulation. The model simulates 
how information spreads through a social network, how citizens evaluate information
from different media sources, and how trust dynamics evolve over time.

The simulation focuses on:
1. Network structure and citizen interactions
2. Media agents with different credibility and bias characteristics
3. Truth assessment and trust dynamics among citizens
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import mesa
import networkx as nx
import numpy as np

from infoflow.agents.base import CitizenAgent, SocialMediaAgent, AgentSet
from infoflow.agents.media.corporate import CorporateMediaAgent
from infoflow.agents.media.government import GovernmentMediaAgent
from infoflow.agents.media.influencer import InfluencerAgent
from infoflow.core.network import create_network
from infoflow.utils.simple_stats import StatsCollector

# Set up module-level logger
logger = logging.getLogger("infoflow.model")


class InformationFlowModel(mesa.Model):
    """
    Core model for simulating information flow in social networks.

    This model creates citizens and media agents, connects them in a network,
    and simulates how information (with varying degrees of accuracy and bias)
    flows through the network and affects truth assessments.
    
    The model features three main types of media agents, with exactly ONE piece of content
    generated from each type (for a total of 3 distinct content pieces in the simulation):
    - Corporate media: Higher credibility, moderate publication rate, broad reach
    - Influencers: Variable credibility, high publication rate, targeted reach
    - Government: High authority, moderate credibility, wide reach
    
    Citizens evaluate information based on:
    - Truth-seeking tendency
    - Confirmation bias
    - Critical thinking skills
    - Social conformity
    
    The model tracks multiple metrics including:
    - Truth assessments (what citizens believe is true)
    - Trust dynamics (how trust in different media sources evolves)
    - Network influence patterns
    
    SIMPLIFIED MODEL: This simulation uses an ultra-simplified approach where:
    1. Only THREE content pieces exist in total (one from each media type)
    2. Duplicate content reception is prevented (citizens ignore repeated content)
    3. Content propagation is clearly visualized via seed nodes
    
    This simplification makes analysis much more tractable while preserving core dynamics.
    """

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
        seed: Optional[int] = None,
    ):
        """
        Initialize the model with the given parameters.

        Args:
            num_citizens: Number of citizen agents to create
            num_corporate_media: Number of corporate media agents to create
            num_influencers: Number of influencer agents to create
            num_government: Number of government media agents to create
            citizen_params: Parameters to use for citizen creation, including:
                - truth_seeking_mean: Mean value for truth-seeking tendency (-5 to 5)
                - truth_seeking_std: Standard deviation for truth-seeking distribution
                - confirmation_bias_min/max: Range for confirmation bias values (0-10)
                - critical_thinking_min/max: Range for critical thinking values (0-10)
                - social_conformity_min/max: Range for social conformity values (0-10)
                - initial_trust_*: Starting trust values for different media types
            media_params: Parameters to use for media creation, including:
                - *_bias_range: Political bias ranges for different media types (-5 to 5)
                - truth_commitment_*: Fact-checking threshold for different media types
                - *_publication_rate: Frequency of content creation per media type
                - *_influence_reach: Portion of citizens reached by each media type
            network_type: Type of network to create:
                - "small_world": Community structure with some long-range connections
                - "scale_free": Network with hubs and power-law degree distribution
                - "random": Random connections between agents
            network_params: Parameters for network creation (specific to network type)
            seed: Random seed for reproducibility
        """
        # Important: Call the superclass constructor with the seed
        super().__init__(seed=seed)

        # Store parameters
        self.num_citizens = num_citizens
        self.num_corporate_media = num_corporate_media
        self.num_influencers = num_influencers
        self.num_government = num_government
        self.network_type = network_type
        
        # Initialize storage for individual agent tracking
        self.agent_snapshots = {}

        # Create a model-specific StatsCollector that won't conflict with the web interface collector
        # This is for internal use only and is completely separate from the collector used for export
        model_run_id = f"model_{int(time.time())}"
        self.stats = StatsCollector(run_id=model_run_id)
        
        # Don't actually start the run - that's handled by the web interface collector
        # This prevents any database interaction from the model's collector
        # self.stats.start_run({}) <- IMPORTANT: Intentionally commented out to avoid duplicate runs

        # Set default parameters if none provided
        self.citizen_params = citizen_params or {
            "truth_seeking_mean": 0,
            "truth_seeking_std": 2.5,
            "confirmation_bias_min": 3,
            "confirmation_bias_max": 8,
            "critical_thinking_min": 3,
            "critical_thinking_max": 8,
            "social_conformity_min": 3,
            "social_conformity_max": 8,
        }

        self.media_params = media_params or {
            "corporate_bias_range": (-3, 3),
            "influencer_bias_range": (-4, 4),
            "government_bias": 1.0,  # Slightly pro-Trump by default
            "truth_commitment_corporate": 6.0,
            "truth_commitment_influencer": 4.0,
            "truth_commitment_government": 5.0,
        }

        self.network_params = network_params or {
            "small_world_k": 4,
            "small_world_p": 0.1,
            "scale_free_m": 3,
            "random_p": 0.1,
        }

        # Create network
        self.G = self._create_network()
        self.grid = mesa.space.NetworkGrid(self.G)

        # Create agents
        self._create_citizen_agents()
        self._create_media_agents()

        # Create agent sets for easy management
        # AgentSet is imported via infoflow.agents.base where we handle the compatibility

        # Print debug information about all agents in the model
        print(f"Model has {len(self.agents)} agents total")
        citizen_count = sum(1 for a in self.agents if isinstance(a, CitizenAgent))
        corporate_count = sum(
            1 for a in self.agents if isinstance(a, CorporateMediaAgent)
        )
        influencer_count = sum(1 for a in self.agents if isinstance(a, InfluencerAgent))
        government_count = sum(
            1 for a in self.agents if isinstance(a, GovernmentMediaAgent)
        )
        print(
            f"Agent counts: {citizen_count} citizens, {corporate_count} corporate, {influencer_count} influencers, {government_count} government"
        )

        # Create set of all citizens
        self.citizens = AgentSet(
            [a for a in self.agents if isinstance(a, CitizenAgent)], random=self.random
        )

        # Create sets for different media types
        self.corporate_medias = AgentSet(
            [a for a in self.agents if isinstance(a, CorporateMediaAgent)],
            random=self.random,
        )

        self.influencers = AgentSet(
            [a for a in self.agents if isinstance(a, InfluencerAgent)],
            random=self.random,
        )

        self.government_medias = AgentSet(
            [a for a in self.agents if isinstance(a, GovernmentMediaAgent)],
            random=self.random,
        )

        # Create combined set of all media agents - IMPORTANT BUG FIX
        # The issue is that we're using isinstance(), but the agents might not actually be
        # instances of SocialMediaAgent due to Mesa 3's way of dynamically creating agent classes
        # So instead we'll check for 'publication_rate' attribute which only media agents have

        # First log the actual agents to see what they are
        media_count = sum(1 for a in self.agents if hasattr(a, "publication_rate"))
        print(
            f"Found {media_count} agents with publication_rate attribute (media agents)"
        )

        # Create the combined set of all media agents
        self.media_agents = AgentSet(
            [a for a in self.agents if hasattr(a, "publication_rate")],
            random=self.random,
        )

        # Log the corrected agent count
        print(f"Created media_agents AgentSet with {len(self.media_agents)} agents")

        # Print debug information about agent sets
        print(
            f"Created agent sets: {len(self.citizens)} citizens, {len(self.corporate_medias)} corporate, {len(self.influencers)} influencers, {len(self.government_medias)} government, {len(self.media_agents)} total media"
        )

        # Setup data collection
        self._setup_data_collection()

        # Don't start stats collection in the database - this is handled by the web interface
        # We'll keep the StatsCollector in memory for model-specific use, but won't write to the DB
        # self.stats.start_run(self._get_parameters_dict())  <- IMPORTANT: Commented out to avoid duplicate runs

    def _create_network(self) -> nx.Graph:
        """
        Create a network of the specified type.

        Returns:
            A networkx graph object
        """
        # Use the dedicated network creation utility
        return create_network(
            network_type=self.network_type,
            num_nodes=self.num_citizens,
            params=self.network_params,
            seed=self.random.randint(0, 10000),
        )

    def _create_citizen_agents(self):
        """Create and place citizen agents in the network."""
        for i in range(self.num_citizens):
            # Create citizen with randomized properties
            agent = CitizenAgent(
                model=self,
                initial_truth_assessment=self.random.random(),  # Random truth assessment between 0-1
                truth_seeking=self.random.gauss(
                    self.citizen_params["truth_seeking_mean"],
                    self.citizen_params["truth_seeking_std"],
                ),
                confirmation_bias=self.random.uniform(
                    self.citizen_params["confirmation_bias_min"],
                    self.citizen_params["confirmation_bias_max"],
                ),
                critical_thinking=self.random.uniform(
                    self.citizen_params["critical_thinking_min"],
                    self.citizen_params["critical_thinking_max"],
                ),
                social_conformity=self.random.uniform(
                    self.citizen_params["social_conformity_min"],
                    self.citizen_params["social_conformity_max"],
                ),
                influence=self.random.uniform(1, 10),  # Random influence
            )

            # Set initial trust levels if provided
            if "initial_trust_in_corporate" in self.citizen_params:
                agent.trust_levels["CorporateMediaAgent"] = self.citizen_params[
                    "initial_trust_in_corporate"
                ]

            if "initial_trust_in_influencers" in self.citizen_params:
                agent.trust_levels["InfluencerAgent"] = self.citizen_params[
                    "initial_trust_in_influencers"
                ]

            if "initial_trust_in_government" in self.citizen_params:
                agent.trust_levels["GovernmentMediaAgent"] = self.citizen_params[
                    "initial_trust_in_government"
                ]

            # Place agent in the network at node i
            self.grid.place_agent(agent, i)

    def _create_media_agents(self):
        """Create media agents of different types."""
        # Create corporate media agents
        for i in range(self.num_corporate_media):
            # Generate political bias within the specified range
            bias_min, bias_max = self.media_params["corporate_bias_range"]
            bias = self.random.uniform(bias_min, bias_max)

            agent = CorporateMediaAgent(
                model=self,
                political_bias=bias,
                truth_commitment=self.media_params["truth_commitment_corporate"],
                # Use publication_rate and influence_reach if provided
                publication_rate=self.media_params.get(
                    "corporate_publication_rate", 0.8
                ),
                influence_reach=self.media_params.get("corporate_influence_reach", 0.7),
            )
            # IMPORTANT: Add agent to the model - this was the missing step!
            # Mesa 3 already adds the agent to model.agents

        # Create influencer agents
        for i in range(self.num_influencers):
            # Generate political bias within the specified range
            bias_min, bias_max = self.media_params["influencer_bias_range"]
            bias = self.random.uniform(bias_min, bias_max)

            agent = InfluencerAgent(
                model=self,
                political_bias=bias,
                truth_commitment=self.media_params["truth_commitment_influencer"],
                # Use publication_rate and influence_reach if provided
                publication_rate=self.media_params.get(
                    "influencer_publication_rate", 0.9
                ),
                influence_reach=self.media_params.get(
                    "influencer_influence_reach", 0.5
                ),
            )
            # IMPORTANT: Add agent to the model - this was the missing step!
            # Mesa 3 already adds the agent to model.agents

        # Create government media agents
        for i in range(self.num_government):
            agent = GovernmentMediaAgent(
                model=self,
                political_bias=self.media_params["government_bias"],
                truth_commitment=self.media_params["truth_commitment_government"],
                # Use publication_rate and influence_reach if provided
                publication_rate=self.media_params.get(
                    "government_publication_rate", 0.7
                ),
                influence_reach=self.media_params.get(
                    "government_influence_reach", 0.6
                ),
            )
            # IMPORTANT: Add agent to the model - this was the missing step!
            # Mesa 3 already adds the agent to model.agents

        # No need to place media agents on the network grid - they're not spatial

        # Debug message about agent creation
        print(f"Created {self.num_corporate_media} corporate media agents")
        print(f"Created {self.num_influencers} influencer agents")
        print(f"Created {self.num_government} government media agents")

    def _setup_data_collection(self):
        """Set up data collection for the model."""
        # Track initial trust values for comparison
        self.initial_trust = {
            "CorporateMediaAgent": 0.0,
            "InfluencerAgent": 0.0,
            "GovernmentMediaAgent": 0.0,
        }

        # Calculate initial average trust values
        if hasattr(self, "citizens") and self.citizens:
            self.initial_trust = {
                "CorporateMediaAgent": np.mean(
                    [
                        a.trust_levels.get("CorporateMediaAgent", 5.0)
                        for a in self.citizens
                    ]
                ),
                "InfluencerAgent": np.mean(
                    [a.trust_levels.get("InfluencerAgent", 5.0) for a in self.citizens]
                ),
                "GovernmentMediaAgent": np.mean(
                    [
                        a.trust_levels.get("GovernmentMediaAgent", 5.0)
                        for a in self.citizens
                    ]
                ),
            }

        # Setup data collector with additional metrics
        self.datacollector = mesa.DataCollector(
            # Model-level metrics
            model_reporters={
                "Average Truth Assessment": lambda m: np.mean(
                    [a.truth_assessment for a in m.citizens]
                ),
                "Truth Assessment Variance": lambda m: np.var(
                    [a.truth_assessment for a in m.citizens]
                ),
                "Trust in Corporate Media": lambda m: np.mean(
                    [a.trust_levels.get("CorporateMediaAgent", 5.0) for a in m.citizens]
                ),
                "Trust in Influencers": lambda m: np.mean(
                    [a.trust_levels.get("InfluencerAgent", 5.0) for a in m.citizens]
                ),
                "Trust in Government": lambda m: np.mean(
                    [
                        a.trust_levels.get("GovernmentMediaAgent", 5.0)
                        for a in m.citizens
                    ]
                ),
                # Add trust variance metrics to show polarization
                "Trust Variance - Corporate": lambda m: np.var(
                    [a.trust_levels.get("CorporateMediaAgent", 5.0) for a in m.citizens]
                ),
                "Trust Variance - Government": lambda m: np.var(
                    [
                        a.trust_levels.get("GovernmentMediaAgent", 5.0)
                        for a in m.citizens
                    ]
                ),
                "Trust Variance - Influencers": lambda m: np.var(
                    [a.trust_levels.get("InfluencerAgent", 5.0) for a in m.citizens]
                ),
            },
            # Agent-level metrics - only collect these for citizen agents
            agent_reporters={
                "Truth Assessment": lambda a: getattr(a, "truth_assessment", None),
                "Truth Seeking": lambda a: getattr(a, "truth_seeking", None),
                "Confirmation Bias": lambda a: getattr(a, "confirmation_bias", None),
                "Trust in Government": lambda a: (
                    getattr(a, "trust_levels", {}).get("GovernmentMediaAgent", 5.0)
                    if hasattr(a, "trust_levels")
                    else None
                ),
                "Trust in Corporate": lambda a: (
                    getattr(a, "trust_levels", {}).get("CorporateMediaAgent", 5.0)
                    if hasattr(a, "trust_levels")
                    else None
                ),
                "Trust in Influencers": lambda a: (
                    getattr(a, "trust_levels", {}).get("InfluencerAgent", 5.0)
                    if hasattr(a, "trust_levels")
                    else None
                ),
            },
        )

        # Collect initial data
        self.datacollector.collect(self)

    def _get_parameters_dict(self):
        """
        Get a dictionary of all model parameters for stats collection.

        Returns:
            Dictionary containing all model parameters
        """
        params = {
            "num_citizens": self.num_citizens,
            "num_corporate_media": self.num_corporate_media,
            "num_influencers": self.num_influencers,
            "num_government": self.num_government,
            "network_type": self.network_type,
        }

        # Add citizen parameters
        for key, value in self.citizen_params.items():
            params[f"citizen_{key}"] = value

        # Add media parameters
        for key, value in self.media_params.items():
            params[f"media_{key}"] = value

        # Add network parameters
        for key, value in self.network_params.items():
            params[f"network_{key}"] = value

        return params

    def _connect_citizens(self):
        """Connect citizen agents based on the network structure."""
        # For each citizen, set their neighbors based on the network
        for i, citizen in enumerate(self.citizens):
            # Use the agent's position in the network
            node_id = i  # We placed citizens at positions 0 to num_citizens-1
            neighbor_nodes = list(self.G.neighbors(node_id))

            # Get the agents at those positions
            citizen.neighbors = []
            for node in neighbor_nodes:
                agents_at_node = self.grid.get_cell_list_contents([node])
                citizen_agents = [
                    a for a in agents_at_node if isinstance(a, CitizenAgent)
                ]
                citizen.neighbors.extend(citizen_agents)

    def _connect_influencers_to_followers(self):
        """Connect influencer agents to random followers."""
        # Each influencer gets some followers from the citizen population
        for influencer in self.influencers:
            # Determine number of followers (between 5-20% of citizens)
            num_followers = self.random.randint(
                max(1, int(self.num_citizens * 0.05)),
                max(2, int(self.num_citizens * 0.2)),
            )

            # Select random citizens as followers
            potential_followers = list(self.citizens)
            self.random.shuffle(potential_followers)
            followers = potential_followers[:num_followers]

            # Add citizens as followers
            for citizen in followers:
                influencer.add_follower(citizen)

    def setup_connections(self):
        """Set up all network connections after agents are created."""
        # Connect citizens based on the network structure
        self._connect_citizens()

        # Connect influencers to followers
        self._connect_influencers_to_followers()

    def _store_agent_snapshots(self):
        """Store snapshots of citizen agents for individual tracking."""
        snapshot = {}
        
        for agent in self.citizens:
            # Store relevant agent properties for tracking
            snapshot[agent.unique_id] = {
                'truth_assessment': agent.truth_assessment,
                'trust_levels': {k: v for k, v in agent.trust_levels.items()},
                'confirmation_bias': agent.confirmation_bias,
                'critical_thinking': agent.critical_thinking,
                'social_conformity': agent.social_conformity,
                'truth_seeking': agent.truth_seeking,
            }
        
        # Store the snapshot for this step
        self.agent_snapshots[self.steps] = snapshot
    
    def step(self):
        """
        Execute one step of the model simulation.
        
        Each step of the model consists of the following sequence:
        1. Media agents create and publish content based on their parameters
        2. Citizen agents process social influence from their network connections
        3. Truth-seeking citizens actively seek information from media sources
        4. Citizens share information with their connections in the network
        5. Data and metrics are collected for analysis
        
        Each step represents a discrete time interval in the simulation where
        all agents perform their actions once.
        """
        print(
            f"\nExecuting model step {self.steps} with {len(self.media_agents)} media agents and {len(self.citizens)} citizens"
        )
        
        # Initialize content tracker if not already present
        if not hasattr(self, "content_tracker"):
            self.content_tracker = {}
            print("Initialized content_tracker in model")
            
        # Initialize duplicate prevention statistics
        if not hasattr(self, "duplicate_prevention_stats"):
            self.duplicate_prevention_stats = {
                "duplicates_prevented": 0,
                "successful_shares": 0
            }
            print("Initialized duplicate prevention statistics")
            
        # Initialize content control flags to limit content to one per media type
        # This enables the "three pieces total" simplified model
        if not hasattr(self, "content_control"):
            self.content_control = {
                "CorporateMediaAgent": {
                    "has_published": False,
                    "representative_published": False
                },
                "InfluencerAgent": {
                    "has_published": False, 
                    "representative_published": False
                },
                "GovernmentMediaAgent": {
                    "has_published": False,
                    "representative_published": False
                }
            }
            print("Initialized content control flags - limiting to one piece per media type")

        # Verify media agents are set up correctly
        if len(self.media_agents) == 0:
            print("ERROR: No media agents found!")
            # Just log the model state for debugging
            media_count = sum(1 for a in self.agents if hasattr(a, "publication_rate"))
            print(f"Found {media_count} agents with publication_rate attribute")

            # Try to fix media agents if they exist but weren't properly added to media_agents
            if media_count > 0:
                from mesa.agent import AgentSet

                corporate_agents = [
                    a
                    for a in self.agents
                    if hasattr(a, "publication_rate")
                    and a.__class__.__name__ == "CorporateMediaAgent"
                ]
                influencer_agents = [
                    a
                    for a in self.agents
                    if hasattr(a, "publication_rate")
                    and a.__class__.__name__ == "InfluencerAgent"
                ]
                government_agents = [
                    a
                    for a in self.agents
                    if hasattr(a, "publication_rate")
                    and a.__class__.__name__ == "GovernmentMediaAgent"
                ]

                self.corporate_medias = AgentSet(corporate_agents, random=self.random)
                self.influencers = AgentSet(influencer_agents, random=self.random)
                self.government_medias = AgentSet(government_agents, random=self.random)

                # Recreate combined set of all media agents - using the fixed approach
                self.media_agents = AgentSet(
                    [a for a in self.agents if hasattr(a, "publication_rate")],
                    random=self.random,
                )

                print(
                    f"Fixed media agents: {len(self.corporate_medias)} corporate, {len(self.influencers)} influencers, {len(self.government_medias)} government, {len(self.media_agents)} total"
                )

        # 1. Media agents create and publish content - with stricter control
        print(f"Stepping {len(self.media_agents)} media agents with content control")
        
        # First, sort media agents by type to process them in groups
        agent_groups = {}
        for agent in self.media_agents:
            agent_type = agent.__class__.__name__
            if agent_type not in agent_groups:
                agent_groups[agent_type] = []
            agent_groups[agent_type].append(agent)
        
        # Now process each media agent category (ensuring only one piece of content per type)
        for agent_type, agents in agent_groups.items():
            if agent_type not in self.content_control:
                print(f"Warning: Unknown agent type {agent_type} - skipping content control")
                for agent in agents:
                    agent.step()
                continue
                
            # Check if this media type has already published its one piece of content
            if self.content_control[agent_type]["has_published"]:
                print(f"Skipping {len(agents)} {agent_type}s - category already published")
                continue
            
            # Only allow one agent to publish content for this category
            if not self.content_control[agent_type]["representative_published"]:
                # Choose a representative agent for this media type
                if agents:
                    chosen_one = self.random.choice(agents)
                    print(f"Stepping REPRESENTATIVE {agent_type} {chosen_one.unique_id} (will publish)")
                    chosen_one.step()
                    # Mark that this category has published its content
                    self.content_control[agent_type]["has_published"] = True
                    self.content_control[agent_type]["representative_published"] = True
                    print(f"✓ {agent_type} has now published its ONE content piece")
                else:
                    print(f"No {agent_type} agents available to publish content")

        # 2. Citizen agents process social influence
        print(f"Processing social influence for {len(self.citizens)} citizens")
        self.citizens.do("be_influenced_by_network")

        # 3. Truth-seeking citizens actively seek information
        print(f"Processing information seeking for {len(self.citizens)} citizens")
        self.citizens.do("seek_information")

        # 4. Citizens share information with their connections
        print(f"Stepping {len(self.citizens)} citizens")
        self.citizens.do("step")

        # Collect data after the step
        self.datacollector.collect(self)
        
        # Store agent snapshots for individual tracking
        self._store_agent_snapshots()

        # Record metrics in stats collector
        self._record_stats()

        # Print trust metrics for debugging
        avg_trust_govt = np.mean(
            [a.trust_levels.get("GovernmentMediaAgent", 5.0) for a in self.citizens]
        )
        avg_trust_corp = np.mean(
            [a.trust_levels.get("CorporateMediaAgent", 5.0) for a in self.citizens]
        )
        print(
            f"After step {self.steps}: Avg govt trust = {avg_trust_govt:.4f}, Avg corp trust = {avg_trust_corp:.4f}"
        )
        
        # Print duplicate prevention statistics
        if hasattr(self, "duplicate_prevention_stats"):
            duplicates_prevented = self.duplicate_prevention_stats["duplicates_prevented"]
            successful_shares = self.duplicate_prevention_stats["successful_shares"]
            total_attempted = duplicates_prevented + successful_shares
            prevention_percentage = 0 if total_attempted == 0 else (duplicates_prevented / total_attempted) * 100
            
            print(f"Duplicate prevention: {duplicates_prevented} duplicates prevented, "
                  f"{successful_shares} successful unique shares "
                  f"({prevention_percentage:.1f}% efficiency gain)")
                  
        # Print content statistics (3 content pieces total)
        if hasattr(self, "content_tracker"):
            content_count = len(self.content_tracker)
            print(f"CONTENT SUMMARY: {content_count} content pieces in circulation")
            
            # Count how many nodes have received each content
            for content_id, content in self.content_tracker.items():
                spread_count = len(content.get("spread_path", []))
                source_type = content.get("source_type", "Unknown")
                accuracy = content.get("accuracy", 0.0)
                content_type = "true" if accuracy >= 0.7 else "false" if accuracy <= 0.3 else "fuzzy"
                
                print(f"  - Content {content_id[-6:]} from {source_type}: "
                      f"Reached {spread_count} nodes, accuracy={accuracy:.2f} ({content_type})")

        # Increment step counter (happens automatically in Mesa 3)

    def _record_stats(self):
        """Record detailed statistics for the current step."""
        metrics = {
            # Trust metrics
            "avg_trust_corporate": np.mean(
                [a.trust_levels.get("CorporateMediaAgent", 5.0) for a in self.citizens]
            ),
            "avg_trust_influencer": np.mean(
                [a.trust_levels.get("InfluencerAgent", 5.0) for a in self.citizens]
            ),
            "avg_trust_government": np.mean(
                [a.trust_levels.get("GovernmentMediaAgent", 5.0) for a in self.citizens]
            ),
            # Trust variance metrics
            "trust_var_corporate": np.var(
                [a.trust_levels.get("CorporateMediaAgent", 5.0) for a in self.citizens]
            ),
            "trust_var_influencer": np.var(
                [a.trust_levels.get("InfluencerAgent", 5.0) for a in self.citizens]
            ),
            "trust_var_government": np.var(
                [a.trust_levels.get("GovernmentMediaAgent", 5.0) for a in self.citizens]
            ),
            # Truth assessment metrics
            "avg_truth_assessment": np.mean(
                [a.truth_assessment for a in self.citizens]
            ),
            "truth_assessment_var": np.var([a.truth_assessment for a in self.citizens]),
            # Min/max metrics
            "min_trust_corporate": min(
                [a.trust_levels.get("CorporateMediaAgent", 5.0) for a in self.citizens]
            ),
            "max_trust_corporate": max(
                [a.trust_levels.get("CorporateMediaAgent", 5.0) for a in self.citizens]
            ),
            "min_trust_government": min(
                [a.trust_levels.get("GovernmentMediaAgent", 5.0) for a in self.citizens]
            ),
            "max_trust_government": max(
                [a.trust_levels.get("GovernmentMediaAgent", 5.0) for a in self.citizens]
            ),
            # Percentile metrics
            "trust_govt_25pct": np.percentile(
                [
                    a.trust_levels.get("GovernmentMediaAgent", 5.0)
                    for a in self.citizens
                ],
                25,
            ),
            "trust_govt_75pct": np.percentile(
                [
                    a.trust_levels.get("GovernmentMediaAgent", 5.0)
                    for a in self.citizens
                ],
                75,
            ),
            # Step number for reference
            "current_step": self.steps,
        }
        
        # Add information spread metrics if content_tracker exists
        if hasattr(self, "content_tracker") and self.content_tracker:
            content_tracker = self.content_tracker
            
            # Calculate spread statistics
            spread_counts = [len(content.get("spread_path", [])) for content in content_tracker.values()]
            
            # Add content metrics
            metrics["total_content_created"] = len(content_tracker)
            metrics["avg_content_spread"] = sum(spread_counts) / len(spread_counts) if spread_counts else 0
            metrics["max_content_spread"] = max(spread_counts) if spread_counts else 0
            
            # Calculate viral content count (content that reached >50% of the network)
            network_size = len(self.citizens)
            viral_threshold = network_size * 0.5
            metrics["viral_content_count"] = sum(1 for count in spread_counts if count >= viral_threshold)
            
            # Source type spread effectiveness
            source_spread = {}
            for content_id, content in content_tracker.items():
                source_type = content.get("source_type", "Unknown")
                if source_type not in source_spread:
                    source_spread[source_type] = []
                source_spread[source_type].append(len(content.get("spread_path", [])))
            
            for source_type, spreads in source_spread.items():
                metrics[f"avg_spread_{source_type}"] = sum(spreads) / len(spreads) if spreads else 0
            
            # Average content accuracy
            accuracies = [content.get("accuracy", 0.5) for content in content_tracker.values()]
            metrics["avg_content_accuracy"] = sum(accuracies) / len(accuracies) if accuracies else 0.5
            
            # Correlation between accuracy and spread
            if spread_counts and accuracies and len(spread_counts) == len(accuracies):
                try:
                    correlation = np.corrcoef(accuracies, spread_counts)[0, 1]
                    metrics["accuracy_spread_correlation"] = correlation
                except:
                    metrics["accuracy_spread_correlation"] = 0
                    
            # Track spread by content accuracy category (true/false/fuzzy)
            content_by_accuracy = {
                "true_content": [],     # accuracy >= 0.7
                "fuzzy_content": [],    # 0.3 < accuracy < 0.7
                "false_content": []     # accuracy <= 0.3
            }
            
            for content_id, content in content_tracker.items():
                accuracy = content.get("accuracy", 0.5)
                spread = len(content.get("spread_path", []))
                
                if accuracy >= 0.7:
                    content_by_accuracy["true_content"].append(spread)
                elif accuracy <= 0.3:
                    content_by_accuracy["false_content"].append(spread)
                else:
                    content_by_accuracy["fuzzy_content"].append(spread)
            
            # Calculate average spread for each content type
            for content_type, spreads in content_by_accuracy.items():
                metrics[f"avg_spread_{content_type}"] = sum(spreads) / len(spreads) if spreads else 0
                
            # Calculate count for each content type
            for content_type, spreads in content_by_accuracy.items():
                metrics[f"count_{content_type}"] = len(spreads)

        # Don't actually record metrics in the database - this would conflict with the web interface
        # We just store them in memory for the model's internal use
        # self.stats.record_step(self.steps, metrics)  <- IMPORTANT: Commented out to avoid duplicate recording


def create_model(
    num_citizens=100,
    num_corporate_media=3,
    num_influencers=5,
    num_government=1,
    network_type="small_world",
    seed=None,
    # Citizen Parameters
    truth_seeking_mean=1.0,
    truth_seeking_std=2.0,
    confirmation_bias_min=4,
    confirmation_bias_max=7,
    critical_thinking_min=4,
    critical_thinking_max=7,
    social_conformity_min=4,
    social_conformity_max=7,
    initial_trust_in_corporate=5.0,
    initial_trust_in_influencers=5.0,
    initial_trust_in_government=5.0,
    # Media Parameters
    corporate_bias_min=-3,
    corporate_bias_max=3,
    influencer_bias_min=-4,
    influencer_bias_max=4,
    government_bias=1.0,
    truth_commitment_corporate=6.0,
    truth_commitment_influencer=4.0,
    truth_commitment_government=5.0,
    # Media Reach Parameters
    # IMPORTANT: Content creation is now strictly limited to THREE pieces total
    # (one from each media type) regardless of the number of media agents.
    # This makes the simulation much easier to analyze.
    corporate_influence_reach=0.7,  # Reach for corporate media
    influencer_influence_reach=0.6,  # Reach for influencers
    government_influence_reach=0.7,  # Reach for government media
    # Network Parameters
    small_world_k=4,
    small_world_p=0.1,
    scale_free_m=3,
    random_p=0.1,
):
    """
    Create and setup a model with customizable parameters.

    This is a convenience function for creating a fully configured model with
    detailed parameter control. It sets up all necessary parameter dictionaries
    and initializes the model with the specified configuration.

    Args:
        num_citizens: Number of citizen agents to create
        num_corporate_media: Number of corporate media agents to create
        num_influencers: Number of influencer agents to create
        num_government: Number of government media agents to create
        network_type: Type of network to create ("small_world", "scale_free", "random")
        seed: Random seed for reproducibility

        # Citizen Cognitive Parameters
        truth_seeking_mean: Mean of truth seeking distribution (-5 to 5)
            Positive values indicate stronger motivation to seek accurate information
            Negative values indicate tendency to avoid challenging information
        truth_seeking_std: Standard deviation of truth seeking distribution
            Higher values create more diverse population of truth attitudes
        confirmation_bias_min: Minimum confirmation bias value (0-10)
            Low values indicate less tendency to favor aligned content
        confirmation_bias_max: Maximum confirmation bias value (0-10)
            High values indicate strong tendency to favor aligned content
        critical_thinking_min: Minimum critical thinking value (0-10)
            Low values indicate less ability to evaluate source credibility
        critical_thinking_max: Maximum critical thinking value (0-10)
            High values indicate strong ability to evaluate source credibility
        social_conformity_min: Minimum social conformity value (0-10)
            Low values indicate less tendency to conform to social circle
        social_conformity_max: Maximum social conformity value (0-10)
            High values indicate strong tendency to conform to social circle
            
        # Citizen Trust Parameters
        initial_trust_in_corporate: Initial trust in corporate media (0-10)
        initial_trust_in_influencers: Initial trust in influencers (0-10)
        initial_trust_in_government: Initial trust in government (0-10)

        # Media Bias Parameters
        corporate_bias_min: Minimum corporate media bias (-5 to 5)
        corporate_bias_max: Maximum corporate media bias (-5 to 5)
        influencer_bias_min: Minimum influencer bias (-5 to 5)
        influencer_bias_max: Maximum influencer bias (-5 to 5)
        government_bias: Government media bias (-5 to 5)
            For all bias parameters: negative values represent anti-Trump bias,
            positive values represent pro-Trump bias, zero represents neutral

        # Media Truth Commitment Parameters
        truth_commitment_corporate: Truth commitment for corporate media (0-10)
        truth_commitment_influencer: Truth commitment for influencers (0-10)
        truth_commitment_government: Truth commitment for government media (0-10)
            Higher values mean stronger fact-checking and accuracy standards

        # Media Publication and Reach Parameters
        corporate_publication_rate: Frequency of content creation for corporate media (0-1)
        corporate_influence_reach: Portion of citizens reached by corporate media (0-1)
        influencer_publication_rate: Frequency of content creation for influencers (0-1)
        influencer_influence_reach: Portion of citizens reached by influencers (0-1)
        government_publication_rate: Frequency of content creation for government media (0-1)
        government_influence_reach: Portion of citizens reached by government media (0-1)

        # Network Parameters
        small_world_k: Number of nearest neighbors in small world network
            Higher values create more densely connected communities
        small_world_p: Rewiring probability in small world network
            Higher values create more random connections between communities
        scale_free_m: Number of edges to add per new node in scale-free network
            Higher values create more hub connections
        random_p: Connection probability in random network
            Higher values create more dense random networks

    Returns:
        A fully configured InformationFlowModel ready for simulation
    """
    # Create parameter dictionaries
    citizen_params = {
        "truth_seeking_mean": truth_seeking_mean,
        "truth_seeking_std": truth_seeking_std,
        "confirmation_bias_min": confirmation_bias_min,
        "confirmation_bias_max": confirmation_bias_max,
        "critical_thinking_min": critical_thinking_min,
        "critical_thinking_max": critical_thinking_max,
        "social_conformity_min": social_conformity_min,
        "social_conformity_max": social_conformity_max,
        "initial_trust_in_corporate": initial_trust_in_corporate,
        "initial_trust_in_influencers": initial_trust_in_influencers,
        "initial_trust_in_government": initial_trust_in_government,
    }

    media_params = {
        "corporate_bias_range": (corporate_bias_min, corporate_bias_max),
        "influencer_bias_range": (influencer_bias_min, influencer_bias_max),
        "government_bias": government_bias,
        "truth_commitment_corporate": truth_commitment_corporate,
        "truth_commitment_influencer": truth_commitment_influencer,
        "truth_commitment_government": truth_commitment_government,
        # Publication rates hardcoded to 1.0 in SocialMediaAgent class
        "corporate_publication_rate": 1.0,  
        "corporate_influence_reach": corporate_influence_reach,
        "influencer_publication_rate": 1.0,
        "influencer_influence_reach": influencer_influence_reach,
        "government_publication_rate": 1.0,
        "government_influence_reach": government_influence_reach,
    }

    network_params = {
        "small_world_k": small_world_k,
        "small_world_p": small_world_p,
        "scale_free_m": scale_free_m,
        "random_p": random_p,
    }

    # Create model with specified parameters
    model = InformationFlowModel(
        num_citizens=num_citizens,
        num_corporate_media=num_corporate_media,
        num_influencers=num_influencers,
        num_government=num_government,
        network_type=network_type,
        citizen_params=citizen_params,
        media_params=media_params,
        network_params=network_params,
        seed=seed,
    )

    # Setup connections
    model.setup_connections()

    return model
