"""
Social media influencer implementation for InfoFlow.

This module defines the social media influencer account type, representing individuals
with dedicated follower networks and high engagement on social platforms.
"""

from typing import Any, Dict, List, Optional

import mesa

from infoflow.agents.base import CitizenAgent
from infoflow.agents.media.base import SocialMediaAgent


class InfluencerAgent(SocialMediaAgent):
    """
    Social media influencers with dedicated follower networks.

    Social media influencers have higher publication rates, lower truth commitment,
    and maintain dedicated follower networks for content distribution. They represent
    popular individual content creators with significant reach on social platforms.
    """

    def __init__(
        self,
        model: mesa.Model,
        political_bias: float = 0.0,
        credibility: float = 5.0,  # Average credibility
        authority: float = 4.0,  # Lower authority than corporate
        truth_commitment: float = 4.0,  # Lower fact checking threshold
        influence_reach: float = 0.4,  # Moderate reach
        publication_rate: float = 0.8,  # Higher publication frequency
        engagement_factor: float = 1.5,
    ):  # How engaging their content is
        """Initialize a social media influencer agent."""
        super().__init__(
            model=model,
            political_bias=political_bias,
            credibility=credibility,
            authority=authority,
            truth_commitment=truth_commitment,
            influence_reach=influence_reach,
            publication_rate=publication_rate,
        )
        self.engagement_factor = engagement_factor
        self.followers = []  # Social media users who follow this influencer

    def add_follower(self, user: CitizenAgent):
        """Add a social media user to this influencer's follower network."""
        if user not in self.followers:
            self.followers.append(user)

    def remove_follower(self, user: CitizenAgent):
        """Remove a social media user from this influencer's follower network."""
        if user in self.followers:
            self.followers.remove(user)

    def create_content(self) -> Dict[str, Any]:
        """
        Create content with higher engagement factor.

        Influencers create more engaging content than other media types.
        """
        content = super().create_content()
        # Add engagement factor to content
        content["engagement_factor"] = self.engagement_factor
        return content

    def broadcast_content(self, content: Dict[str, Any]) -> List[CitizenAgent]:
        """
        Distribute content to followers with high engagement.

        Args:
            content: Content object to broadcast

        Returns:
            List of social media users who received the content
        """
        # If we have dedicated followers, send to them
        reached_users = []
        if self.followers:
            for follower in self.followers:
                follower.receive_information(content, self)
                reached_users.append(follower)

        # Also reach some non-followers based on influence_reach
        users = getattr(self.model, "citizens", [])
        if users:
            # Filter out followers to avoid duplicates
            non_followers = [u for u in users if u not in self.followers]
            if non_followers:
                # Reach a percentage of non-followers based on influence_reach
                num_to_reach = int(len(non_followers) * (self.influence_reach / 2))
                if num_to_reach > 0:
                    # Use the model's random generator
                    indices = list(range(len(non_followers)))
                    self.model.random.shuffle(indices)
                    selected_indices = indices[:num_to_reach]

                    selected_users = [non_followers[i] for i in selected_indices]

                    for user in selected_users:
                        user.receive_information(content, self)

                    reached_users.extend(selected_users)
        
        # Track seed nodes for this content - only select a small subset as seeds
        try:
            if "content_id" in content and reached_users:
                # Store seed nodes for this content
                if not hasattr(self.model, "content_seed_nodes"):
                    self.model.content_seed_nodes = {}
                
                # Select only a small subset of users as seed nodes (limited to max 5 and min 1)
                max_seed_nodes = max(1, min(5, int(len(reached_users) * 0.1)))
                
                # Create a copy of the list to avoid modifying the original
                potential_seeds = list(reached_users)
                self.model.random.shuffle(potential_seeds)
                selected_seeds = potential_seeds[:max_seed_nodes]
                
                # Extract unique_ids safely
                seed_node_ids = []
                for user in selected_seeds:
                    if hasattr(user, "unique_id"):
                        seed_node_ids.append(user.unique_id)
                
                # Only store if we have valid seed nodes
                if seed_node_ids:
                    self.model.content_seed_nodes[content["content_id"]] = seed_node_ids
                    print(f"Influencer: Marked {len(seed_node_ids)} seed nodes out of {len(reached_users)} recipients")
        except Exception as e:
            print(f"Error tracking seed nodes in influencer media: {e}")

        return reached_users
