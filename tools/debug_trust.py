#!/usr/bin/env python3
"""
Debug script for testing the trust update mechanism in CitizenAgent.

This script creates a simple test model and citizen agents, then directly
calls trust update with controlled parameters to verify functionality.
"""

import sys
import os
import numpy as np
import mesa
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug_trust.log", mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("debug_trust")

# Configure trust_dynamics logger specifically
trust_logger = logging.getLogger("trust_dynamics")
trust_logger.setLevel(logging.DEBUG)
trust_file_handler = logging.FileHandler("trust_dynamics.log", mode='w')
trust_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
trust_logger.addHandler(trust_file_handler)

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import InfoFlow classes
from infoflow.agents.base import CitizenAgent
from infoflow.core.model import InformationFlowModel


class SimpleTrustModel(mesa.Model):
    """Simple model for testing trust updates."""
    
    def __init__(self):
        # Important: Call the superclass constructor with seed parameter
        super().__init__(seed=42)
        # In Mesa 3, agents are stored directly in agents list and AgentSet
        self.citizens = []


def test_direct_trust_update():
    """Test trust update function directly with controlled inputs."""
    logger.info("=== TESTING DIRECT TRUST UPDATE ===")
    
    # Create a simple model
    model = SimpleTrustModel()
    
    # Create agents with different critical thinking values
    agents = []
    critical_thinking_values = [1.0, 5.0, 10.0]
    
    for i, ct_value in enumerate(critical_thinking_values):
        agent = CitizenAgent(model, critical_thinking=ct_value)
        # In Mesa 3, we need to add the agent to the model
        if not hasattr(model, 'agents'):
            # Mesa 3 automatically creates this, but our simple model may not have it
            from mesa.agent import AgentSet
            model.agents = AgentSet(agent_class=CitizenAgent, model=model)
        model.agents.add(agent)
        agents.append(agent)
        logger.info(f"Created CitizenAgent {agent.unique_id} with critical_thinking={ct_value}")
    
    # Test source types
    source_types = ["CorporateMediaAgent", "InfluencerAgent", "GovernmentMediaAgent"]
    
    # Test accuracy values
    accuracy_values = [0.1, 0.3, 0.5, 0.7, 0.9]
    
    # Run direct trust update tests
    for agent in agents:
        for source_type in source_types:
            initial_trust = agent.trust_levels.get(source_type, 5.0)
            logger.info(f"Agent {agent.unique_id} initial trust for {source_type}: {initial_trust}")
            
            for accuracy in accuracy_values:
                # Make a copy of current trust before update
                before_update = agent.trust_levels.get(source_type, 5.0)
                
                # Directly call trust update
                logger.info(f"Calling update_trust with source_type={source_type}, perceived_accuracy={accuracy:.2f}")
                agent.update_trust(source_type, accuracy)
                
                # Log the result
                after_update = agent.trust_levels.get(source_type, 5.0)
                trust_change = after_update - before_update
                logger.info(f"Trust changed from {before_update:.4f} to {after_update:.4f} (delta: {trust_change:.4f})")
                
                # Check that trust actually changed
                if abs(trust_change) < 0.0001:
                    logger.warning(f"WARNING: Trust did not change for agent {agent.unique_id}, source_type={source_type}, accuracy={accuracy:.2f}")


def test_content_reception():
    """Test trust update through content reception."""
    logger.info("\n=== TESTING CONTENT RECEPTION ===")
    
    # Create a simple model
    model = SimpleTrustModel()
    
    # Create a test agent
    agent = CitizenAgent(model)
    # In Mesa 3, we need to add the agent to the model
    if not hasattr(model, 'agents'):
        # Mesa 3 automatically creates this, but our simple model may not have it
        from mesa.agent import AgentSet
        model.agents = AgentSet(agent_class=CitizenAgent, model=model)
    model.agents.add(agent)
    logger.info(f"Created test CitizenAgent {agent.unique_id}")
    
    # Create test content with different accuracies
    test_contents = []
    
    for accuracy in [0.1, 0.5, 0.9]:
        for source_type in ["CorporateMediaAgent", "InfluencerAgent", "GovernmentMediaAgent"]:
            content = {
                "accuracy": accuracy,
                "framing_bias": 0.0,
                "source_type": source_type,
                "source_credibility": 0.7,
                "source_authority": 0.6
            }
            test_contents.append(content)
    
    # Log initial trust levels
    for source_type in ["CorporateMediaAgent", "InfluencerAgent", "GovernmentMediaAgent"]:
        logger.info(f"Initial trust for {source_type}: {agent.trust_levels.get(source_type, 5.0)}")
    
    # Process content items
    content_acceptance_count = 0
    
    for content in test_contents:
        source_type = content["source_type"]
        accuracy = content["accuracy"]
        
        # Log before trust level
        before_trust = agent.trust_levels.get(source_type, 5.0)
        logger.info(f"Before receiving content: Trust for {source_type} = {before_trust:.4f}")
        
        # Create a dummy source agent
        class DummySource:
            def __init__(self):
                self.__class__.__name__ = source_type
                self.unique_id = 999  # Dummy ID
        
        # Receive content
        logger.info(f"Receiving content with accuracy={accuracy:.2f}, source_type={source_type}")
        accepted = agent.receive_information(content, DummySource())
        
        # Log after trust level
        after_trust = agent.trust_levels.get(source_type, 5.0)
        trust_change = after_trust - before_trust
        logger.info(f"After receiving content: Trust for {source_type} = {after_trust:.4f} (delta: {trust_change:.4f})")
        logger.info(f"Content accepted: {accepted}")
        
        if accepted:
            content_acceptance_count += 1
            
            # Check that trust actually changed
            if abs(trust_change) < 0.0001:
                logger.warning(f"WARNING: Content was accepted but trust did not change for source_type={source_type}, accuracy={accuracy:.2f}")
    
    # Log summary
    logger.info(f"Content acceptance summary: {content_acceptance_count} out of {len(test_contents)} items accepted")


def test_full_model_trust():
    """Test trust updates in a complete model simulation."""
    logger.info("\n=== TESTING FULL MODEL TRUST UPDATES ===")
    
    # Import the create_model helper function from the module
    from infoflow.core.model import create_model
    
    # Create a full information flow model with extreme parameters to force trust changes
    model = create_model(
        num_citizens=5,  # Small number for easier tracking
        num_corporate_media=1,
        num_influencers=1,
        num_government=1,
        network_type="small_world",
        
        # Set extreme publication rates to ensure content is created
        corporate_publication_rate=1.0,    # Always publish
        influencer_publication_rate=1.0,   # Always publish
        government_publication_rate=1.0,   # Always publish
        
        # Set extreme influence reach to ensure content reaches citizens
        corporate_influence_reach=1.0,     # Reach all citizens
        influencer_influence_reach=1.0,    # Reach all citizens
        government_influence_reach=1.0,    # Reach all citizens
        
        # Set extreme truth commitments for clear difference in accuracy
        truth_commitment_corporate=0.0,    # Very inaccurate content
        truth_commitment_influencer=5.0,   # Moderate accuracy
        truth_commitment_government=10.0,  # Very accurate content
        
        # Set extreme political bias values
        corporate_bias_min=-5.0,           # Strong anti-Trump bias
        corporate_bias_max=-5.0,           # Strong anti-Trump bias (same to ensure consistency)
        influencer_bias_min=0.0,           # Neutral bias
        influencer_bias_max=0.0,           # Neutral bias (same to ensure consistency)
        government_bias=5.0,               # Strong pro-Trump bias
        
        # Set critical thinking high to amplify trust changes
        critical_thinking_min=10.0,        # Maximum critical thinking
        critical_thinking_max=10.0,        # Maximum critical thinking
        
        # Set trust seeking high to focus on accuracy
        truth_seeking_mean=5.0,            # Maximum truth seeking
        truth_seeking_std=0.0,             # No variation
        
        # Set extreme initial trust values to see changes more clearly
        initial_trust_in_corporate=2.0,
        initial_trust_in_influencers=5.0,
        initial_trust_in_government=8.0,
        
        # Use a fixed seed for reproducibility
        seed=42
    )
    
    # Log initial trust levels
    logger.info("Initial trust levels:")
    for i, citizen in enumerate(model.citizens):  # Log all citizens
        for source_type in ["CorporateMediaAgent", "InfluencerAgent", "GovernmentMediaAgent"]:
            logger.info(f"Citizen {citizen.unique_id} trust for {source_type}: {citizen.trust_levels.get(source_type, 5.0)}")
    
    # Store initial trust values for comparison
    initial_trusts = {
        "CorporateMediaAgent": [c.trust_levels.get("CorporateMediaAgent", 5.0) for c in model.citizens],
        "InfluencerAgent": [c.trust_levels.get("InfluencerAgent", 5.0) for c in model.citizens],
        "GovernmentMediaAgent": [c.trust_levels.get("GovernmentMediaAgent", 5.0) for c in model.citizens]
    }
    
    # Run 10 steps
    for step in range(10):
        logger.info(f"\nExecuting model step {step+1}")
        model.step()
        
        # Log trust levels after each step
        logger.info(f"Trust levels after step {step+1}:")
        for i, citizen in enumerate(model.citizens):  # Log all citizens
            for source_type in ["CorporateMediaAgent", "InfluencerAgent", "GovernmentMediaAgent"]:
                current_trust = citizen.trust_levels.get(source_type, 5.0)
                initial_trust = initial_trusts[source_type][i]
                change = current_trust - initial_trust
                logger.info(f"Citizen {citizen.unique_id} trust for {source_type}: {current_trust:.4f} (change: {change:+.4f})")
    
    # Analyze average trust changes
    logger.info("\nAnalyzing average trust changes across all citizens:")
    final_trusts = {
        "CorporateMediaAgent": [c.trust_levels.get("CorporateMediaAgent", 5.0) for c in model.citizens],
        "InfluencerAgent": [c.trust_levels.get("InfluencerAgent", 5.0) for c in model.citizens],
        "GovernmentMediaAgent": [c.trust_levels.get("GovernmentMediaAgent", 5.0) for c in model.citizens]
    }
    
    any_trust_changed = False
    
    for source_type in ["CorporateMediaAgent", "InfluencerAgent", "GovernmentMediaAgent"]:
        initial_avg = np.mean(initial_trusts[source_type])
        final_avg = np.mean(final_trusts[source_type])
        change_avg = final_avg - initial_avg
        max_change = np.max(np.abs(np.array(final_trusts[source_type]) - np.array(initial_trusts[source_type])))
        
        logger.info(f"{source_type}:")
        logger.info(f"  Average initial trust: {initial_avg:.4f}")
        logger.info(f"  Average final trust: {final_avg:.4f}")
        logger.info(f"  Average change: {change_avg:+.4f}")
        logger.info(f"  Maximum change for any citizen: {max_change:.4f}")
        
        if max_change > 0.001:
            any_trust_changed = True
    
    if not any_trust_changed:
        logger.warning("NO TRUST CHANGES DETECTED despite extreme parameter values!")
    else:
        logger.info("Trust changes detected - trust dynamics are functioning!")
        
    return any_trust_changed


if __name__ == "__main__":
    logger.info("Starting trust update debugging")
    
    # Run the tests
    logger.info("=== TESTING DIRECT TRUST UPDATE FUNCTION ===")
    test_direct_trust_update()
    
    logger.info("\n=== TESTING CONTENT RECEPTION ===")
    test_content_reception()
    
    logger.info("\n=== TESTING FULL MODEL SIMULATION ===")
    trust_changed = test_full_model_trust()
    
    # Print summary
    logger.info("\n=== DEBUGGING SUMMARY ===")
    if trust_changed:
        logger.info("SUCCESS: Trust changes were detected in the full model simulation.")
        logger.info("This suggests the update_trust function is working correctly when called.")
        logger.info("The issue might be in media content distribution or content acceptance.")
    else:
        logger.info("ISSUE DETECTED: No trust changes were detected in any test.")
        logger.info("Possible causes:")
        logger.info("1. update_trust function is not being called")
        logger.info("2. Media agents are not publishing content")
        logger.info("3. Citizens are not receiving content from media agents")
        logger.info("4. Content is being received but not accepted (acceptance_factor too low)")
        
    logger.info("\nCheck the trust_dynamics.log file for detailed logs.")
    logger.info("Trust update debugging complete")