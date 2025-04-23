"""
Base social media account agent for InfoFlow.

This module defines the foundation for all social media account types
(corporate accounts, influencers, and government accounts) in the simulation.
"""

from typing import Any, Dict, List, Optional

import mesa

from infoflow.agents.base import BaseAgent, CitizenAgent


class SocialMediaAgent(BaseAgent):
    """
    Base class for all social media account types (corporate, influencer, government).

    Attributes:
        political_bias (float): -5 to 5 scale (anti-Trump to pro-Trump)
        credibility (float): 0-10 scale of perceived reliability
        authority (float): 0-10 scale of institutional influence
        truth_commitment (float): 0-10 scale of fact-checking threshold
        influence_reach (float): 0-1 scale of proportion of social media users reached
        publication_rate (float): 0-1 scale of frequency of content creation
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
        # Base accuracy tied to truth commitment - dramatically different curve
        # For truth commitment < 3: accuracy drops sharply
        # For truth commitment > 7: accuracy rises sharply
        if self.truth_commitment < 3.0:
            # Very low accuracy for low truth commitment (0.0 to 0.3)
            base_accuracy = (self.truth_commitment / 10.0) * 0.3
        elif self.truth_commitment > 7.0:
            # Very high accuracy for high truth commitment (0.7 to 0.9)
            base_accuracy = 0.7 + (self.truth_commitment - 7.0) / 10.0 * 0.2
        else:
            # Moderate middle range (0.3 to 0.7)
            base_accuracy = 0.3 + (self.truth_commitment - 3.0) / 4.0 * 0.4

        # Apply much smaller randomness - more consistent outcomes
        random_generator = self.model.random
        random_range = 0.1
        actual_accuracy = min(
            1.0,
            max(
                0.0,
                base_accuracy + random_generator.uniform(-random_range, random_range),
            ),
        )

        # Political bias (anti-Trump to pro-Trump scale) directly becomes the framing bias
        # We keep it on the -5 to 5 scale in the content for consistency with the spec

        # Generate a unique content ID
        content_id = f"content_{self.unique_id}_{getattr(self.model, 'steps', 0)}_{random_generator.randint(0, 10000)}"
        
        return {
            "content_id": content_id,                # Unique identifier for tracking
            "accuracy": actual_accuracy,
            "framing_bias": self.political_bias,     # Keep as -5 to 5 scale
            "source_authority": self.authority / 10.0,
            "source_credibility": self.credibility / 10.0,
            "source_type": self.__class__.__name__,
            "created_step": getattr(self.model, "steps", 0),  # When content was created
            "origin_id": self.unique_id,             # Original creator
            "spread_path": [self.unique_id],         # Tracks path through network
        }

    def publish_content(self) -> Optional[Dict[str, float]]:
        """Check if content should be published.
        
        For simplicity, each media agent will only publish once during the entire simulation.
        This drastically reduces content volume while preserving core dynamics.

        Returns:
            Content if published, None otherwise
        """
        # Initialize has_published flag if it doesn't exist
        if not hasattr(self, 'has_published'):
            self.has_published = False
            
        # Only publish once per simulation, with 100% probability (publication_rate no longer used)
        if not self.has_published:
            self.has_published = True
            return self.create_content()
        return None

    def broadcast_content(self, content: Dict[str, float]) -> List[CitizenAgent]:
        """Distribute content to appropriate social media users.

        Args:
            content: Content object to broadcast

        Returns:
            List of social media users who received the content
        """
        # Implementation placeholder - logic will differ by social media account type
        return []

    def step(self):
        """Execute one step of the social media account agent."""
        # Debug info about stepping process
        print(
            f"[DEBUG] SocialMediaAgent.step: {self.__class__.__name__} {self.unique_id} with publication_rate={self.publication_rate}"
        )

        # Check if we should publish content this step
        content = self.publish_content()

        # If content was created, broadcast it
        if content:
            print(
                f"[DEBUG] SocialMediaAgent.step: {self.__class__.__name__} {self.unique_id} created content, broadcasting..."
            )
            recipients = self.broadcast_content(content)
            print(
                f"[DEBUG] SocialMediaAgent.step: {self.__class__.__name__} {self.unique_id} broadcasted to {len(recipients)} social media users"
            )
        else:
            print(
                f"[DEBUG] SocialMediaAgent.step: {self.__class__.__name__} {self.unique_id} did not create content this step"
            )
