"""
Government social media account implementation for InfoFlow.

This module defines the government social media account type, representing official
government sources on social platforms with high authority and moderate credibility.
"""

from typing import Any, Dict, List, Optional

import mesa

from infoflow.agents.base import CitizenAgent
from infoflow.agents.media.base import SocialMediaAgent


class GovernmentMediaAgent(SocialMediaAgent):
    """
    Official government social media accounts.

    Government social media accounts have the highest authority, lower publication rate,
    and political bias aligned with the current administration. These represent official
    government communications channels on social media platforms.
    """

    def __init__(
        self,
        model: mesa.Model,
        political_bias: float = 0.0,  # Set based on gov't alignment
        credibility: float = 6.0,  # Above average credibility
        authority: float = 9.0,  # Highest authority
        truth_commitment: float = 5.0,  # Variable fact checking
        influence_reach: float = 0.6,  # High reach
        publication_rate: float = 0.3,
    ):  # Lower publication frequency
        """Initialize a government social media account agent."""
        super().__init__(
            model=model,
            political_bias=political_bias,
            credibility=credibility,
            authority=authority,
            truth_commitment=truth_commitment,
            influence_reach=influence_reach,
            publication_rate=publication_rate,
        )

    def create_content(self) -> Dict[str, Any]:
        """
        Create content with higher authority impact.

        Government social media content carries additional authority weight, which is
        diminished if truth commitment is low (simulating reduced authority
        when government communications are perceived as unreliable).
        """
        content = super().create_content()

        # Calculate authority factor based on truth commitment
        # Much more dramatic effect - low truth commitment severely reduces authority
        if self.truth_commitment < 3.0:
            # Very low authority for low truth commitment (0.5 to 0.8)
            authority_scaling = 0.5 + (self.truth_commitment / 3.0) * 0.3
        elif self.truth_commitment > 7.0:
            # Very high authority for high truth commitment (1.2 to 1.5)
            authority_scaling = 1.2 + (self.truth_commitment - 7.0) / 3.0 * 0.3
        else:
            # Progressive scaling in the middle (0.8 to 1.2)
            authority_scaling = 0.8 + (self.truth_commitment - 3.0) / 4.0 * 0.4

        content["authority_factor"] = authority_scaling

        return content

    def broadcast_content(self, content: Dict[str, Any]) -> List[CitizenAgent]:
        """
        Distribute content with high authority impact.

        Government social media accounts reach a wide audience with high authority.

        Args:
            content: Content object to broadcast

        Returns:
            List of social media users who received the content
        """
        # Get all social media users from the model
        users = getattr(self.model, "citizens", [])
        if not users:
            return []

        # Determine how many users to reach based on influence_reach
        num_to_reach = int(len(users) * self.influence_reach)

        # Select random social media users to reach
        if num_to_reach > 0:
            # Use the model's random generator
            indices = list(range(len(users)))
            self.model.random.shuffle(indices)
            selected_indices = indices[:num_to_reach]

            selected_users = [users[i] for i in selected_indices]

            # Track seed nodes for this content - only select a small subset as true seed nodes
            try:
                if "content_id" in content:
                    # Store seed nodes for this content
                    if not hasattr(self.model, "content_seed_nodes"):
                        self.model.content_seed_nodes = {}
                    
                    # Limit number of seed nodes to avoid overcrowding the visualization
                    # Choose between 1-5 nodes, approximately 10% of recipients
                    max_seed_nodes = max(1, min(5, int(len(selected_users) * 0.1)))
                    
                    # Randomly sample from selected users to get a smaller seed node set
                    seed_indices = self.model.random.sample(range(len(selected_users)), max_seed_nodes) if len(selected_users) > max_seed_nodes else range(len(selected_users))
                    
                    # Extract unique_ids safely
                    seed_node_ids = []
                    for idx in seed_indices:
                        user = selected_users[idx]
                        if hasattr(user, "unique_id"):
                            seed_node_ids.append(user.unique_id)
                    
                    # Only store if we have valid seed nodes
                    if seed_node_ids:
                        self.model.content_seed_nodes[content["content_id"]] = seed_node_ids
                        print(f"Government media: Marked {len(seed_node_ids)} seed nodes out of {len(selected_users)} recipients")
            except Exception as e:
                print(f"Error tracking seed nodes in government media: {e}")
            
            # Send content to selected social media users
            for user in selected_users:
                user.receive_information(content, self)

            return selected_users

        return []
