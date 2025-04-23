"""
Corporate social media account implementation for InfoFlow.

This module defines the corporate social media account type, representing 
established media organizations with wide reach and moderate to high credibility
on social media platforms.

Corporate media in this simulation:
- Have broader but untargeted distribution (reaching many citizens randomly)
- Possess higher average credibility and authority than other media types
- Maintain moderate to high fact-checking standards (truth commitment)
- Typically have more balanced political bias distribution
- Influence citizens through broad information dissemination

Examples include traditional news organizations' social media accounts,
mainstream media outlets, and established digital news publishers.
"""

from typing import Any, Dict, List, Optional

import mesa

from infoflow.agents.base import CitizenAgent
from infoflow.agents.media.base import SocialMediaAgent


class CorporateMediaAgent(SocialMediaAgent):
    """
    Corporate social media accounts with broad reach and moderate credibility.

    Corporate social media accounts represent established news organizations and 
    media outlets operating on social platforms. They are characterized by:
    
    - Higher institutional credibility (compared to influencers)
    - Greater perceived authority from institutional backing
    - Wide but untargeted audience reach (broadcasting model)
    - Moderate to high commitment to factual accuracy
    - More balanced political bias distribution than other media types
    - Moderate content publication frequency
    
    These agents distribute content broadly to random selections of citizens
    rather than to specific follower groups, simulating mainstream media's
    broadcasting approach on social platforms.
    """

    def __init__(
        self,
        model: mesa.Model,
        political_bias: float = 0.0,
        credibility: float = 7.0,  # Higher average credibility
        authority: float = 7.0,  # Higher average authority
        truth_commitment: float = 6.0,  # Moderate-to-high fact checking
        influence_reach: float = 0.7,  # Wide reach
        publication_rate: float = 0.5,
    ):  # Moderate publication frequency
        """Initialize a corporate social media account agent."""
        super().__init__(
            model=model,
            political_bias=political_bias,
            credibility=credibility,
            authority=authority,
            truth_commitment=truth_commitment,
            influence_reach=influence_reach,
            publication_rate=publication_rate,
        )

    def broadcast_content(self, content: Dict[str, float]) -> List[CitizenAgent]:
        """
        Distribute content to a wide audience based on influence_reach.

        Corporate media agents use a broad distribution approach:
        1. Randomly select a portion of citizens based on influence_reach
        2. Deliver content to each selected citizen
        3. Track how many citizens accept the information

        This simulates how established media organizations distribute content on
        social platforms - reaching a wide but random audience rather than targeting
        specific demographic or psychographic segments.

        Args:
            content: Content object to broadcast containing attributes:
                - accuracy: Truth value (0-1 scale)
                - framing_bias: Political bias (-5 to 5 scale)
                - source_authority: Perceived legitimacy (0-1 scale)
                - source_credibility: Perceived reliability (0-1 scale)
                - source_type: The class name of this agent

        Returns:
            List of citizens who received the content (whether accepted or not)
        """
        import logging

        logger = logging.getLogger("broadcast")
        logger.debug(
            f"[DEBUG] CorporateMediaAgent {self.unique_id}: Broadcasting content with accuracy={content.get('accuracy', 0.5):.4f}"
        )

        # Get all social media users from the model
        users = getattr(self.model, "citizens", [])
        if not users:
            logger.warning(
                f"[WARNING] CorporateMediaAgent {self.unique_id}: No social media users found in model!"
            )
            return []

        # Determine how many users to reach based on influence_reach
        num_to_reach = int(len(users) * self.influence_reach)
        logger.debug(
            f"[DEBUG] CorporateMediaAgent {self.unique_id}: Trying to reach {num_to_reach} social media users out of {len(users)} (influence_reach={self.influence_reach:.2f})"
        )

        # Select random social media users to reach
        if num_to_reach > 0:
            # Use the model's random generator
            indices = list(range(len(users)))
            self.model.random.shuffle(indices)
            selected_indices = indices[:num_to_reach]

            selected_users = [users[i] for i in selected_indices]

            # Count content acceptance
            acceptance_count = 0

            # Send content to selected social media users
            # Track seed nodes for this content - only the INITIAL recipients from media agent
            # These users are the true "seed nodes" - first to receive the content
            try:
                if "content_id" in content:
                    # Store seed nodes for this content
                    if not hasattr(self.model, "content_seed_nodes"):
                        self.model.content_seed_nodes = {}
                    
                    # Extract unique_ids safely - limit to 10% of users to avoid overcrowding
                    max_seed_nodes = max(1, min(5, int(len(selected_users) * 0.1)))
                    seed_indices = self.model.random.sample(range(len(selected_users)), max_seed_nodes) if len(selected_users) > max_seed_nodes else range(len(selected_users))
                    
                    seed_node_ids = []
                    for idx in seed_indices:
                        user = selected_users[idx]
                        if hasattr(user, "unique_id"):
                            seed_node_ids.append(user.unique_id)
                    
                    # Only store if we have valid seed nodes
                    if seed_node_ids:
                        self.model.content_seed_nodes[content["content_id"]] = seed_node_ids
                        print(f"Corporate media: Marked {len(seed_node_ids)} seed nodes out of {len(selected_users)} recipients")
            except Exception as e:
                print(f"Error tracking seed nodes in corporate media: {e}")
            
            for user in selected_users:
                accepted = user.receive_information(content, self)
                if accepted:
                    acceptance_count += 1

            logger.debug(
                f"[DEBUG] CorporateMediaAgent {self.unique_id}: Content accepted by {acceptance_count} out of {len(selected_users)} social media users"
            )
            return selected_users

        return []
