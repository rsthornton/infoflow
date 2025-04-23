"""
Base agent classes for the InfoFlow model.

This module defines the foundation for all agent types in the simulation,
including shared functionality and data structures. The module contains:

1. CitizenAgent: Represents social media users who consume, process, and share
   content. They possess cognitive attributes like truth-seeking tendency,
   confirmation bias, critical thinking, and social conformity.

2. SocialMediaAgent: Base class for different types of media sources (corporate,
   influencer, and government) that create and distribute content with varying
   degrees of accuracy and bias.

3. AgentSet: A utility class for managing collections of agents with similar
   properties and behaviors.

These agent types interact in a network to simulate information flow and the
evolution of truth assessments and trust dynamics in social media environments.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import mesa
import numpy as np

# Handle both Mesa 2 and Mesa 3 imports
try:
    from mesa.agent import AgentSet  # Mesa 3
except ImportError:
    try:
        from mesa.agent_set import AgentSet  # Mesa 2
    except ImportError:
        # Create a simple fallback implementation for compatibility
        class AgentSet(list):
            def __init__(self, agents, random=None):
                super().__init__(agents)
                self.random = random
                
            def do(self, method_name, *args, **kwargs):
                for agent in self:
                    getattr(agent, method_name)(*args, **kwargs)
                    
            def filter(self, condition):
                return AgentSet([a for a in self if condition(a)], self.random)

# Set up module-level logger
logger = logging.getLogger("trust_dynamics")


class BaseAgent(mesa.Agent):
    """Base class for all agent types in the simulation."""

    def __init__(self, model: mesa.Model):
        """Initialize the base agent with common attributes.

        Args:
            model: Model instance the agent belongs to
        """
        # Note: unique_id is automatically assigned in Mesa 3
        super().__init__(model)

    def step(self):
        """Base step method to be implemented by subclasses."""
        pass


class CitizenAgent(BaseAgent):
    """
    Social media users who consume, process, and share content from various sources.

    Attributes:
        truth_assessment (float): 0-1 scale assessment of truth about the current topic (0.5 is neutral)
        confidence (float): 0-10 scale strength of truth assessment
        truth_seeking (float): -5 to 5 scale of truth-seeking attitude
        confirmation_bias (float): 0-10 scale tendency to favor aligned content
        critical_thinking (float): 0-10 scale ability to evaluate source credibility
        influence (float): 0-10 scale impact on connected users
        social_conformity (float): 0-10 scale tendency to align with social circle
        trust_levels (dict): Dictionary tracking trust in different social media account types
    """

    def __init__(
        self,
        model: mesa.Model,
        initial_truth_assessment: float = 0.5,
        confidence: float = 5.0,
        truth_seeking: float = 0.0,
        confirmation_bias: float = 5.0,
        critical_thinking: float = 5.0,
        influence: float = 5.0,
        social_conformity: float = 5.0,
    ):
        """Initialize a social media user agent.

        Args:
            model: Model instance the agent belongs to
            initial_truth_assessment: Starting truth assessment value (0-1 scale)
            confidence: Strength of truth assessment (0-10 scale)
            truth_seeking: Attitude toward truth (-5 to 5 scale)
            confirmation_bias: Tendency to favor aligned content (0-10 scale)
            critical_thinking: Ability to evaluate source credibility (0-10 scale)
            influence: Impact on connected users (0-10 scale)
            social_conformity: Tendency to align with social circle (0-10 scale)
        """
        super().__init__(model)

        # Core truth assessment attributes
        self.truth_assessment = initial_truth_assessment
        self.confidence = confidence

        # Cognitive attributes
        self.truth_seeking = truth_seeking
        self.confirmation_bias = confirmation_bias
        self.critical_thinking = critical_thinking
        self.influence = influence
        self.social_conformity = social_conformity

        # Trust tracking for different social media account types
        self.trust_levels = {
            "CorporateMediaAgent": 5.0,  # Corporate social media accounts
            "InfluencerAgent": 5.0,      # Social media influencers
            "GovernmentMediaAgent": 5.0, # Government social media accounts
        }

        # Content memory (recent information received)
        self.content_memory = []
        
        # Set to track content IDs that have been received to prevent duplicates
        self.received_content_ids = set()

        # Network relationships - will be populated by the model
        self.neighbors = []

    def receive_information(self, content: Dict[str, Any], source: BaseAgent) -> bool:
        """Process incoming information.

        Args:
            content: Dictionary containing content properties
            source: Source agent who created the content

        Returns:
            Whether the content was accepted (truth assessment updated)
        """
        logger.debug(
            f"[DEBUG] CitizenAgent {self.unique_id}: receive_information called with content from {source.__class__.__name__}"
        )
        
        # Initialize content tracker if needed
        if not hasattr(self.model, "content_tracker"):
            self.model.content_tracker = {}
        
        # Check if content has ID and if we've already processed it
        if "content_id" in content:
            content_id = content["content_id"]
            
            # Skip if already received - prevent duplicate processing
            if content_id in self.received_content_ids:
                logger.debug(
                    f"[DEBUG] CitizenAgent {self.unique_id}: Already received content {content_id}, skipping"
                )
                # Increment the duplicates prevented counter if it exists
                if hasattr(self.model, "duplicate_prevention_stats"):
                    self.model.duplicate_prevention_stats["duplicates_prevented"] += 1
                return False
                
            # If content isn't in tracker yet, add it
            if content_id not in self.model.content_tracker:
                self.model.content_tracker[content_id] = content
            
            # Get the reference to use
            content_ref = self.model.content_tracker[content_id]
            
            # Update tracking info in the central copy
            content_ref["last_shared_step"] = getattr(self.model, "steps", 0)
            
            # Add this agent to spread path if not already there
            if "spread_path" in content_ref and self.unique_id not in content_ref["spread_path"]:
                content_ref["spread_path"].append(self.unique_id)
                
            # Mark this content as received for future duplicate prevention
            self.received_content_ids.add(content_id)
        else:
            # For content without ID (rare), use as is - can't track duplicates
            content_ref = content
        
        # Add content reference to memory (limited capacity)
        self.content_memory.append({"content": content_ref, "source": source})
        if len(self.content_memory) > 10:  # Keep only 10 most recent items
            self.content_memory.pop(0)

        # Step 1: Extract content properties
        content_accuracy = content.get("accuracy", 0.5)
        content_bias = content.get("framing_bias", 0.0)
        source_type = content.get("source_type", "Unknown")
        source_credibility = content.get("source_credibility", 0.5)
        source_authority = content.get("source_authority", 0.5)

        logger.debug(
            f"[DEBUG] CitizenAgent {self.unique_id}: Processing content with accuracy={content_accuracy:.4f}, bias={content_bias:.4f}, source_type={source_type}"
        )

        # Optional factors that might be present
        engagement_factor = content.get("engagement_factor", 1.0)
        authority_factor = content.get("authority_factor", 1.0)

        # Step 2: Apply source trust filter
        source_trust = self.trust_levels.get(source_type, 5.0) / 10.0
        trust_weight = source_trust * source_credibility * authority_factor
        logger.debug(
            f"[DEBUG] CitizenAgent {self.unique_id}: Trust weight = {trust_weight:.4f} (source_trust={source_trust:.4f}, credibility={source_credibility:.4f}, authority_factor={authority_factor:.4f})"
        )

        # Step 3: Calculate confirmation bias effect
        # Measure alignment between content bias and agent truth assessment
        # For anti-Trump to pro-Trump bias, we still need to calculate alignment
        # High confirmation bias means preferring aligned content
        # Convert truth_assessment (0-1) to a bias scale (-1 to 1) for comparison with content bias
        truth_assessment_as_bias = (self.truth_assessment - 0.5) * 2
        # Normalize content_bias from -5 to 5 scale to -1 to 1 scale for comparison
        normalized_content_bias = content_bias / 5.0
        truth_assessment_alignment = 1.0 - abs(
            truth_assessment_as_bias - normalized_content_bias
        )
        confirmation_effect = (
            truth_assessment_alignment * self.confirmation_bias
        ) / 10.0

        # Step 4: Apply critical thinking to evaluate accuracy
        # Higher critical thinking reduces trust in low-credibility sources
        # and increases trust in high-credibility sources
        critical_adjustment = (
            (self.critical_thinking / 10.0) * (source_credibility - 0.5) * 2
        )

        # Calculate overall content acceptance probability
        acceptance_factor = (
            (trust_weight * 0.4)  # 40% based on trust
            + (confirmation_effect * 0.4)  # 40% based on confirmation bias
            + (critical_adjustment * 0.2)  # 20% based on critical thinking
            + 0.2  # Add 20% base acceptance rate to ensure more trust updates
        )

        # Apply engagement factor if present (influencers)
        acceptance_factor *= engagement_factor

        # Ensure acceptance factor is in valid range (0-1)
        acceptance_factor = min(1.0, max(0.0, acceptance_factor))

        # Step 5: Decide whether to accept the content
        # Higher acceptance factor means more likely to update truth assessment
        random_value = self.model.random.random()
        content_accepted = random_value < acceptance_factor

        logger.debug(
            f"[DEBUG] CitizenAgent {self.unique_id}: Acceptance check: random={random_value:.4f}, acceptance_factor={acceptance_factor:.4f}, accepted={content_accepted}"
        )

        if content_accepted:
            logger.debug(
                f"[DEBUG] CitizenAgent {self.unique_id}: Content ACCEPTED - updating truth assessment and trust"
            )

            # Step 6: Update truth assessment if content is accepted
            # Calculate how much to move truth assessment toward content bias
            # Truth seekers (positive values) are more influenced by content accuracy
            # Truth avoiders (negative values) are more influenced by content bias

            # Convert truth_seeking to a 0-1 scale for calculations
            truth_seeking_factor = (self.truth_seeking + 5) / 10.0

            # Balance between accuracy and bias based on truth_seeking
            accuracy_weight = 0.5 + (truth_seeking_factor * 0.5)
            bias_weight = 1.0 - accuracy_weight

            # Calculate target truth assessment
            # Truth seekers (positive values) weight accuracy more
            # Truth avoiders (negative values) weight alignment with current truth assessments more

            # For truth seekers:
            # - Content accuracy should directly influence their truth assessment
            # - Political bias should have less influence

            # For truth avoiders:
            # - Content that aligns with their existing truth assessments is more accepted
            # - Political bias that matches their own bias has more influence

            # Political bias can still affect perception, but it's a bias on how
            # content is interpreted, not a direct shift of truth assessment

            # Calculate how political bias affects perception of accuracy
            # Strong bias in either direction can distort perception of truth
            bias_distortion = (
                abs(content_bias) / 10.0
            )  # 0-0.5 scale based on bias magnitude

            # Truth-seeking agents are less affected by political bias
            bias_distortion = bias_distortion * (1 - (truth_seeking_factor * 0.5))

            # Calculate perceived accuracy (accuracy distorted by political bias)
            perceived_accuracy = content_accuracy * (1 - bias_distortion)
            logger.debug(
                f"[DEBUG] CitizenAgent {self.unique_id}: Perceived accuracy={perceived_accuracy:.4f} (content_accuracy={content_accuracy:.4f}, bias_distortion={bias_distortion:.4f})"
            )

            # Target truth assessment is primarily based on perceived accuracy (truth value)
            # with some influence from confirmation bias
            target_truth_assessment = perceived_accuracy

            # Move truth assessment toward target based on confidence (inverse relationship)
            # Lower confidence means more movement
            truth_assessment_movement = (1.0 - (self.confidence / 10.0)) * 0.3

            # Update truth assessment
            old_truth_assessment = self.truth_assessment
            self.truth_assessment = self.truth_assessment + (
                (target_truth_assessment - self.truth_assessment)
                * truth_assessment_movement
            )
            # Ensure truth assessment stays in 0-1 range
            self.truth_assessment = max(0.0, min(1.0, self.truth_assessment))

            logger.debug(
                f"[DEBUG] CitizenAgent {self.unique_id}: Truth assessment updated: {old_truth_assessment:.4f} → {self.truth_assessment:.4f} (change of {self.truth_assessment - old_truth_assessment:.4f})"
            )

            # Step 7: Adjust confidence based on truth assessment change
            truth_assessment_change = abs(self.truth_assessment - old_truth_assessment)

            # Large changes decrease confidence slightly
            if truth_assessment_change > 0.1:
                old_confidence = self.confidence
                self.confidence = max(1.0, self.confidence - 0.5)
                logger.debug(
                    f"[DEBUG] CitizenAgent {self.unique_id}: Large change in truth assessment, decreasing confidence: {old_confidence:.1f} → {self.confidence:.1f}"
                )
            # Small changes with high trust increase confidence slightly
            elif trust_weight > 0.7:
                old_confidence = self.confidence
                self.confidence = min(10.0, self.confidence + 0.3)
                logger.debug(
                    f"[DEBUG] CitizenAgent {self.unique_id}: Small change with high trust, increasing confidence: {old_confidence:.1f} → {self.confidence:.1f}"
                )

            # Step 8: Update trust in source
            logger.debug(
                f"[DEBUG] CitizenAgent {self.unique_id}: Calling update_trust for {source_type} with accuracy {content_accuracy:.4f}"
            )
            self.update_trust(source_type, content_accuracy)
        else:
            logger.debug(
                f"[DEBUG] CitizenAgent {self.unique_id}: Content REJECTED - no trust update"
            )

        return content_accepted

    def update_trust(self, source_type: str, perceived_accuracy: float):
        """Update trust in a source type based on perceived accuracy.

        Args:
            source_type: Type of source (string)
            perceived_accuracy: How accurate the agent perceives the content (0-1)
        """
        logger.debug(
            f"[DEBUG] CitizenAgent {self.unique_id}: update_trust called for {source_type} with accuracy {perceived_accuracy:.4f}"
        )

        # If source type is not in trust_levels, initialize it
        if source_type not in self.trust_levels:
            self.trust_levels[source_type] = 5.0
            logger.debug(
                f"[DEBUG] CitizenAgent {self.unique_id}: Source type {source_type} not in trust_levels, initializing to 5.0"
            )

        current_trust = self.trust_levels[source_type]
        logger.debug(
            f"[DEBUG] CitizenAgent {self.unique_id}: Current trust for {source_type} = {current_trust:.4f}"
        )

        # Calculate trust adjustment based on perceived accuracy
        # Much more dramatic effect - this will make trust changes very noticeable

        # Convert accuracy to a dramatic scale
        # Below 0.4 = very inaccurate, above 0.6 = very accurate
        if perceived_accuracy < 0.4:
            # Strong negative impact for low accuracy
            accuracy_impact = (
                -1.0 - (0.4 - perceived_accuracy) * 5.0
            )  # Range: -1.0 to -3.0
            logger.debug(
                f"[DEBUG] CitizenAgent {self.unique_id}: Low accuracy {perceived_accuracy:.4f}, negative impact: {accuracy_impact:.4f}"
            )
        elif perceived_accuracy > 0.6:
            # Strong positive impact for high accuracy
            accuracy_impact = (
                1.0 + (perceived_accuracy - 0.6) * 5.0
            )  # Range: 1.0 to 3.0
            logger.debug(
                f"[DEBUG] CitizenAgent {self.unique_id}: High accuracy {perceived_accuracy:.4f}, positive impact: {accuracy_impact:.4f}"
            )
        else:
            # Small impact for middle accuracy
            accuracy_impact = (perceived_accuracy - 0.5) * 4.0  # Range: -0.4 to 0.4
            logger.debug(
                f"[DEBUG] CitizenAgent {self.unique_id}: Medium accuracy {perceived_accuracy:.4f}, small impact: {accuracy_impact:.4f}"
            )

        # Critical thinkers adjust trust even more based on accuracy
        # Very high at max critical thinking (10)
        critical_factor = 0.5 + (self.critical_thinking / 10.0)  # Range: 0.5 to 1.5
        logger.debug(
            f"[DEBUG] CitizenAgent {self.unique_id}: Critical thinking factor: {critical_factor:.4f} (critical_thinking={self.critical_thinking:.1f})"
        )

        # Calculate trust adjustment - much more significant now
        trust_adjustment = (
            accuracy_impact * critical_factor
        )  # Range: roughly -4.5 to 4.5
        logger.debug(
            f"[DEBUG] CitizenAgent {self.unique_id}: Trust adjustment = {trust_adjustment:.4f}"
        )

        # Apply adjustment - allow bigger swings
        new_trust = max(0.0, min(10.0, current_trust + trust_adjustment))
        logger.debug(
            f"[DEBUG] CitizenAgent {self.unique_id}: New trust for {source_type} = {new_trust:.4f} (was {current_trust:.4f}, change of {new_trust - current_trust:.4f})"
        )

        # Store the updated trust value
        self.trust_levels[source_type] = new_trust

    def share_information(self) -> Optional[Dict[str, Any]]:
        """Share content with connections.

        Returns:
            The content to be shared (or None if not sharing)
        """
        # If no content in memory, nothing to share
        if not self.content_memory:
            return None

        # Decide whether to share based on confidence
        # Higher confidence increases sharing probability
        share_probability = self.confidence / 20.0  # Range: 0 to 0.5

        # Only share if random check passes
        if self.model.random.random() > share_probability:
            return None

        # Select content to share, preferring content that aligns with truth assessments
        potential_shares = []
        for memory_item in self.content_memory:
            content = memory_item["content"]

            # Calculate alignment based on accuracy vs truth assessment
            # Truth assessments represent how true the agent thinks claims are (0-1)
            content_accuracy = content.get("accuracy", 0.5)

            # Alignment is how close the content's accuracy is to agent's truth assessment
            # A high-truth_assessment agent prefers accurate content, low-truth_assessment prefers inaccurate
            alignment = 1.0 - abs(self.truth_assessment - content_accuracy)

            # Political bias still matters for alignment, but differently
            # Higher confirmation bias means agent prefers content with matching political bias
            if self.confirmation_bias > 5.0:  # Higher confirmation bias
                # Get content political bias
                content_bias = content.get(
                    "framing_bias", 0.0
                )  # -5 to 5 scale (anti-Trump to pro-Trump)

                # Infer agent's preferred political bias based on past content in memory
                # Default to neutral if no clear preference
                preferred_bias = 0.0
                bias_counts = {"positive": 0, "negative": 0}

                # Count positive/negative bias content in memory to infer preference
                for memory in self.content_memory:
                    past_bias = memory["content"].get("framing_bias", 0.0)
                    if past_bias > 1.0:  # Pro-Trump leaning
                        bias_counts["positive"] += 1
                    elif past_bias < -1.0:  # Anti-Trump leaning
                        bias_counts["negative"] += 1

                # Infer preference if there's a clear pattern
                if bias_counts["positive"] > bias_counts["negative"]:
                    preferred_bias = 3.0  # Prefer pro-Trump
                elif bias_counts["negative"] > bias_counts["positive"]:
                    preferred_bias = -3.0  # Prefer anti-Trump

                # Calculate political alignment (1.0 = perfect match, 0.0 = opposite)
                bias_alignment = 1.0 - min(
                    1.0, abs(preferred_bias - content_bias) / 10.0
                )

                # Blend accuracy alignment with political bias alignment
                # Higher confirmation bias gives more weight to political alignment
                confirmation_factor = self.confirmation_bias / 10.0
                alignment = (alignment * (1.0 - confirmation_factor)) + (
                    bias_alignment * confirmation_factor
                )

            # Store content with its alignment score
            potential_shares.append((alignment, content))

        # Sort by alignment (highest first)
        # Use the alignment value (first item in tuple) as the sort key
        potential_shares.sort(key=lambda x: x[0], reverse=True)

        # Select content to share (usually highest alignment)
        if not potential_shares:
            return None

        # Important change: Instead of creating a copy, we reference the original content
        # from the model.content_tracker dictionary to ensure we're using a single instance
        if self.model.random.random() < 0.8 and len(potential_shares) > 0:
            original_content = potential_shares[0][1]
        else:
            original_content = self.model.random.choice(potential_shares)[1]
        
        # Get the content_id to reference the central copy
        content_id = original_content.get("content_id")
        
        # If this content has a valid ID and is in the global tracker, use the reference
        if content_id and hasattr(self.model, "content_tracker") and content_id in self.model.content_tracker:
            # Use the central copy from the content tracker
            selected_content = self.model.content_tracker[content_id]
            
            # Update the spread path to include this agent
            if "spread_path" in selected_content and self.unique_id not in selected_content["spread_path"]:
                selected_content["spread_path"].append(self.unique_id)
                
            # Update the last_shared_step
            selected_content["last_shared_step"] = getattr(self.model, "steps", 0)
            
            # Note: We're no longer doing content modification (bias adjustment, accuracy degradation)
            # to avoid creating multiple versions. This simplifies the model but preserves core dynamics.
            
            # We also don't modify the source information anymore
            return selected_content
        else:
            # If for some reason we don't have a content tracker or this content isn't in it,
            # log this unusual situation
            print(f"Warning: Content sharing requested for content not in tracker: {content_id}")
            return None

    def be_influenced_by_network(self):
        """Update truth assessments based on connections."""
        # If no connections, no influence
        if not self.neighbors:
            return

        # Collect truth assessments from connections, weighted by their influence
        weighted_truth_assessments = []
        total_weight = 0

        for neighbor in self.neighbors:
            # Influence acts as weight
            weight = neighbor.influence
            weighted_truth_assessments.append((neighbor.truth_assessment, weight))
            total_weight += weight

        # If no valid weights, return
        if total_weight == 0:
            return

        # Calculate weighted average truth assessment
        network_truth_assessment = (
            sum(
                truth_assessment * weight
                for truth_assessment, weight in weighted_truth_assessments
            )
            / total_weight
        )

        # Update own truth assessment based on social_conformity
        # Higher social_conformity means more influenced by network
        conformity_factor = self.social_conformity / 10.0  # Range: 0 to 1

        # Only apply small adjustment per step (max 10% of the difference)
        truth_assessment_adjustment = (
            (network_truth_assessment - self.truth_assessment) * conformity_factor * 0.1
        )

        # Update truth assessment
        self.truth_assessment = max(
            0.0, min(1.0, self.truth_assessment + truth_assessment_adjustment)
        )

    def seek_information(self):
        """Actively seek new information (for truth-seeking agents)."""
        # Only truth-seeking agents above a threshold actively seek information
        if self.truth_seeking <= 1.0:
            return
            
        # IMPORTANT: For simplified simulations, we don't want citizens to create
        # new content. Instead, we'll have them reuse existing content from the
        # content tracker, or do nothing if no content exists yet.
        
        # Don't create new content if we can avoid it to keep content volume minimal
        if hasattr(self.model, "content_tracker") and self.model.content_tracker:
            # Reuse existing content from the content tracker
            available_content = list(self.model.content_tracker.values())
            
            # Filter out content already received by this agent
            unread_content = []
            for content in available_content:
                if "content_id" in content and content["content_id"] not in self.received_content_ids:
                    unread_content.append(content)
            
            # If there's unread content available, randomly select one
            if unread_content:
                # Select a random piece of unread content
                selected_content = self.model.random.choice(unread_content)
                
                # Determine the original source agent
                source_type = selected_content.get("source_type", "CorporateMediaAgent")
                
                # Find a media agent of this type
                for agent in self.model.agents:
                    if hasattr(agent, "publication_rate") and agent.__class__.__name__ == source_type:
                        # Use the original content with this source
                        self.receive_information(selected_content, agent)
                        return
            else:
                # All content already received, so nothing to do
                return
                        
        # Legacy code only used as fallback if no content exists yet
        # Get available media sources from the model
        media_sources = []
        for source_type in [
            "CorporateMediaAgent",
            "InfluencerAgent",
            "GovernmentMediaAgent",
        ]:
            if hasattr(self.model, source_type.lower().replace("agent", "s")):
                media_set = getattr(
                    self.model, source_type.lower().replace("agent", "s")
                )
                if media_set:
                    media_sources.extend(media_set)

        if not media_sources:
            return

        # Only proceed with small probability (0.1%) to minimize content creation
        if self.model.random.random() > 0.001:
            return

        # Select a source based on trust levels
        trust_levels = [
            self.trust_levels.get(agent.__class__.__name__, 5.0)
            for agent in media_sources
        ]

        # Calculate total trust for normalization
        total_trust = sum(trust_levels)
        if total_trust == 0:
            return

        # Normalize to probabilities
        probabilities = [trust / total_trust for trust in trust_levels]

        # Select source
        selected_source = self.model.random.choices(
            media_sources, weights=probabilities, k=1
        )[0]

        # Request content directly - with very low probability (emergency fallback)
        if selected_source:
            content = selected_source.create_content()
            self.receive_information(content, selected_source)

    def step(self):
        """Execute one step of the social media user agent."""
        # Process social influence from connected users
        self.be_influenced_by_network()

        # Share content with connections
        shared_content = self.share_information()
        if shared_content and self.neighbors:
            # Only try to share if the content has an ID (trackable)
            if "content_id" in shared_content:
                content_id = shared_content["content_id"]
                
                # Share with neighbors who haven't seen it yet
                share_count = 0
                # Find neighbors who haven't received this content yet
                unaware_neighbors = [n for n in self.neighbors 
                                    if not hasattr(n, "received_content_ids") 
                                    or content_id not in n.received_content_ids]
                                    
                # Early exit if no neighbors need the content
                if not unaware_neighbors:
                    if hasattr(self.model, "duplicate_prevention_stats"):
                        self.model.duplicate_prevention_stats["duplicates_prevented"] += len(self.neighbors)
                    return
                
                # Share with neighbors who haven't seen it
                for neighbor in unaware_neighbors:
                    result = neighbor.receive_information(shared_content, self)
                    if result:
                        share_count += 1
                        # Track successful shares
                        if hasattr(self.model, "duplicate_prevention_stats"):
                            self.model.duplicate_prevention_stats["successful_shares"] += 1
                
                # Log sharing activity if any occurred
                if share_count > 0:
                    logger.debug(
                        f"[DEBUG] CitizenAgent {self.unique_id}: Shared content {content_id} with {share_count} neighbors who hadn't seen it yet"
                    )
            else:
                # For content without IDs (rare), share with all neighbors
                for neighbor in self.neighbors:
                    neighbor.receive_information(shared_content, self)

        # Truth-seeking behavior - actively looking for content
        self.seek_information()


class SocialMediaAgent(BaseAgent):
    """
    Base class for all social media account types (corporate, influencer, government).
    
    These agents represent information sources in the social media environment.
    Each type of media agent creates and distributes content with different 
    characteristics based on its parameters. The content they produce has varying
    degrees of accuracy and political framing bias.
    
    Media agents influence citizen beliefs through:
    - Content accuracy (affected by truth commitment)
    - Political framing (affected by political bias)
    - Distribution patterns (affected by influence reach)
    - Publishing frequency (affected by publication rate)
    
    The credibility and authority attributes affect how citizens evaluate and 
    trust content from these sources.

    Attributes:
        political_bias (float): -5 to 5 scale (anti-Trump to pro-Trump)
            Negative values represent anti-Trump bias
            Positive values represent pro-Trump bias
            Zero represents neutral political stance
        credibility (float): 0-10 scale of perceived reliability
            Higher values mean more citizens trust the source initially
        authority (float): 0-10 scale of institutional influence
            Higher values mean the source has more societal legitimacy
        truth_commitment (float): 0-10 scale of fact-checking threshold
            Higher values mean more accurate content is produced on average
        influence_reach (float): 0-1 scale of proportion of social media users reached
            Higher values mean content reaches more citizens
        publication_rate (float): 0-1 scale of frequency of content creation
            Higher values mean content is created more frequently
    """

    def __init__(
        self,
        model: mesa.Model,
        political_bias: float = 0.0,
        credibility: float = 5.0,
        authority: float = 5.0,
        truth_commitment: float = 5.0,
        influence_reach: float = 0.5,
        publication_rate: float = 0.5,
    ):
        """Initialize a social media account agent.

        Args:
            model: Model instance the agent belongs to
            political_bias: Political leaning (-5 to 5 scale)
            credibility: Perceived reliability (0-10 scale)
            authority: Institutional influence (0-10 scale)
            truth_commitment: Fact-checking threshold (0-10 scale)
            influence_reach: Proportion of social media users reached (0-1 scale)
            publication_rate: Frequency of content creation (0-1 scale)
        """
        super().__init__(model)

        self.political_bias = political_bias
        self.credibility = credibility
        self.authority = authority
        self.truth_commitment = truth_commitment
        self.influence_reach = influence_reach
        self.publication_rate = publication_rate

    def create_content(self) -> Dict[str, float]:
        """Create content based on agent properties.

        Returns:
            Content object with properties like accuracy, framing_bias, etc.
        """
        # Base accuracy tied to truth commitment
        base_accuracy = self.truth_commitment / 10.0

        # Apply randomness using Mesa 3's random generator via the model
        random_generator = self.model.random
        actual_accuracy = min(
            1.0, max(0.0, base_accuracy + random_generator.uniform(-0.2, 0.2))
        )

        # Political bias (anti-Trump to pro-Trump scale) directly becomes the framing bias
        # We keep it on the -5 to 5 scale in the content for consistency with the spec

        return {
            "accuracy": actual_accuracy,
            "framing_bias": self.political_bias,  # Keep as -5 to 5 scale
            "source_authority": self.authority / 10.0,
            "source_credibility": self.credibility / 10.0,
            "source_type": self.__class__.__name__,
        }

    def publish_content(self) -> Optional[Dict[str, float]]:
        """Check if content should be published this step based on publication_rate.

        Returns:
            Content if published, None otherwise
        """

        random_value = self.model.random.random()
        should_publish = random_value < self.publication_rate

        logger.debug(
            f"[DEBUG] {self.__class__.__name__} {self.unique_id}: Publication check: random={random_value:.4f}, rate={self.publication_rate:.4f}, should_publish={should_publish}"
        )

        if should_publish:
            content = self.create_content()
            logger.debug(
                f"[DEBUG] {self.__class__.__name__} {self.unique_id}: Created content with accuracy={content.get('accuracy', 0.5):.4f}"
            )
            return content
        return None

    def broadcast_content(self, content: Dict[str, float]) -> List[CitizenAgent]:
        """Distribute content to appropriate social media users.

        Args:
            content: Content object to broadcast

        Returns:
            List of social media users who received the content
        """
        logger.debug(
            f"[DEBUG] {self.__class__.__name__} {self.unique_id}: Broadcasting content to social media users"
        )

        # Implementation placeholder - logic will differ by agent type
        # This will be overridden by specific media agent types
        return []

    def step(self):
        """Execute one step of the social media account agent."""

        # Check if we should publish content this step
        content = self.publish_content()

        # If content was created, broadcast it
        if content:
            recipients = self.broadcast_content(content)
            logger.debug(
                f"[DEBUG] {self.__class__.__name__} {self.unique_id}: Content broadcasted to {len(recipients)} social media users"
            )
