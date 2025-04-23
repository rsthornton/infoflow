"""
Data collection utilities for InfoFlow social media simulation.
"""

from typing import Any, Dict, List, Optional
import numpy as np

from infoflow.utils.helpers import calculate_variance
from infoflow.data.metrics import calculate_polarization, calculate_opinion_clusters


class DataCollector:
    """Collects and stores simulation data."""

    def __init__(self, model):
        """Initialize with the model to collect data from."""
        self.model = model
        self.data = {
            # Time series data lists
            "mean_truth_assessment": [],
            "truth_assessment_variance": [],
            "trust_in_CorporateMediaAgent": [],
            "trust_in_InfluencerAgent": [],
            "trust_in_GovernmentMediaAgent": [],
            "polarization_over_time": [],
            "opinion_clusters_over_time": [],
            
            # Current snapshot data will be added as needed
        }

    def collect_truth_assessment_metrics(self):
        """Collect metrics related to truth assessment distribution."""
        citizens = self.model.citizens
        truth_assessments = [agent.truth_assessment for agent in citizens]
        
        # Store current truth assessments for distribution analysis
        self.data["current_truth_assessments"] = truth_assessments
        
        # Calculate and store time series metrics
        mean_truth = sum(truth_assessments) / len(truth_assessments) if truth_assessments else 0
        variance = calculate_variance(truth_assessments)
        
        self.data["mean_truth_assessment"].append(mean_truth)
        self.data["truth_assessment_variance"].append(variance)
        
        # Calculate polarization and opinion clusters
        polarization = calculate_polarization(truth_assessments)
        opinion_clusters = calculate_opinion_clusters(truth_assessments)
        
        self.data["polarization_over_time"].append(polarization)
        self.data["opinion_clusters_over_time"].append(opinion_clusters)

    def collect_trust_metrics(self):
        """Collect metrics related to trust levels."""
        citizens = self.model.citizens
        
        # Calculate average trust for each source type
        for source_type in [
            "CorporateMediaAgent",
            "InfluencerAgent",
            "GovernmentMediaAgent",
        ]:
            trust_values = [agent.trust_levels.get(source_type, 5.0) for agent in citizens]
            
            # Store current trust values for distribution analysis
            self.data[f"current_trust_in_{source_type}"] = trust_values
            
            # Calculate and store time series metrics
            avg_trust = sum(trust_values) / len(trust_values) if trust_values else 5.0
            self.data[f"trust_in_{source_type}"].append(avg_trust)

    def collect_cognitive_parameters(self):
        """Collect data about agent cognitive parameters."""
        citizens = self.model.citizens
        
        # Store current parameter values for distribution analysis
        self.data["current_confirmation_bias"] = [agent.confirmation_bias for agent in citizens]
        self.data["current_critical_thinking"] = [agent.critical_thinking for agent in citizens]
        self.data["current_social_conformity"] = [agent.social_conformity for agent in citizens]
        self.data["current_truth_seeking"] = [agent.truth_seeking for agent in citizens]
        self.data["current_influence"] = [agent.influence for agent in citizens]
        self.data["current_confidence"] = [agent.confidence for agent in citizens]

    def collect_content_metrics(self):
        """Collect metrics related to content sharing and propagation."""
        # Check if content tracker exists in the model
        if not hasattr(self.model, "content_tracker"):
            return
            
        content_tracker = self.model.content_tracker
        
        # Total number of content pieces created
        self.data["total_content_created"] = len(content_tracker)
        
        # Calculate spread statistics
        spread_counts = [len(content.get("spread_path", [])) for content in content_tracker.values()]
        
        # Average content spread
        self.data["avg_content_spread"] = sum(spread_counts) / len(spread_counts) if spread_counts else 0
        
        # Maximum content spread
        self.data["max_content_spread"] = max(spread_counts) if spread_counts else 0
        
        # Calculate viral content count (content that reached >50% of the network)
        network_size = len(self.model.citizens) if hasattr(self.model, "citizens") else 100
        viral_threshold = network_size * 0.5
        self.data["viral_content_count"] = sum(1 for count in spread_counts if count >= viral_threshold)
        
        # Content by source type
        content_by_source = {}
        for content in content_tracker.values():
            source_type = content.get("source_type", "Unknown")
            if source_type not in content_by_source:
                content_by_source[source_type] = 0
            content_by_source[source_type] += 1
            
        self.data["content_by_source"] = content_by_source
        
        # Source type spread effectiveness (avg spread per source)
        source_spread = {}
        for content_id, content in content_tracker.items():
            source_type = content.get("source_type", "Unknown")
            if source_type not in source_spread:
                source_spread[source_type] = []
            source_spread[source_type].append(len(content.get("spread_path", [])))
        
        for source_type, spreads in source_spread.items():
            self.data[f"avg_spread_{source_type}"] = sum(spreads) / len(spreads) if spreads else 0
        
        # Average content accuracy
        accuracies = [content.get("accuracy", 0.5) for content in content_tracker.values()]
        self.data["avg_content_accuracy"] = sum(accuracies) / len(accuracies) if accuracies else 0.5
        
        # Track correlation between content accuracy and spread
        if spread_counts and accuracies and len(spread_counts) == len(accuracies):
            try:
                import numpy as np
                correlation = np.corrcoef(accuracies, spread_counts)[0, 1]
                self.data["accuracy_spread_correlation"] = correlation
            except:
                self.data["accuracy_spread_correlation"] = 0
                
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
            self.data[f"avg_spread_{content_type}"] = sum(spreads) / len(spreads) if spreads else 0
            
        # Calculate count for each content type
        for content_type, spreads in content_by_accuracy.items():
            self.data[f"count_{content_type}"] = len(spreads)

    def collect_all(self):
        """Collect all metrics."""
        self.collect_truth_assessment_metrics()
        self.collect_trust_metrics()
        self.collect_cognitive_parameters()
        self.collect_content_metrics()
        return self.data
        
    def get_agent_snapshots(self):
        """Get agent snapshot data from the model if available."""
        if hasattr(self.model, "agent_snapshots"):
            return self.model.agent_snapshots
        return None
        
    def get_agent_metrics(self, agent_id):
        """
        Extract metrics for a specific agent over time from snapshots.
        
        Args:
            agent_id: The unique ID of the agent
            
        Returns:
            Dictionary with time series data for the agent
        """
        snapshots = self.get_agent_snapshots()
        if not snapshots:
            return None
            
        agent_metrics = {
            "truth_assessment": [],
            "trust_levels": {
                "CorporateMediaAgent": [],
                "InfluencerAgent": [],
                "GovernmentMediaAgent": [],
            },
            "confirmation_bias": [],
            "critical_thinking": [],
            "social_conformity": [],
            "truth_seeking": [],
        }
        
        # Extract data from each time step
        for step in sorted(snapshots.keys()):
            if agent_id in snapshots[step]:
                agent_data = snapshots[step][agent_id]
                
                # Extract metrics
                agent_metrics["truth_assessment"].append(agent_data.get("truth_assessment", 0.5))
                
                for source_type in agent_metrics["trust_levels"].keys():
                    agent_metrics["trust_levels"][source_type].append(
                        agent_data.get("trust_levels", {}).get(source_type, 5.0)
                    )
                
                agent_metrics["confirmation_bias"].append(agent_data.get("confirmation_bias", 5.0))
                agent_metrics["critical_thinking"].append(agent_data.get("critical_thinking", 5.0))
                agent_metrics["social_conformity"].append(agent_data.get("social_conformity", 5.0))
                agent_metrics["truth_seeking"].append(agent_data.get("truth_seeking", 0.0))
                
        return agent_metrics