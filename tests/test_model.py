"""
Tests for the central model class in InfoFlow.

This module contains tests to verify that the InformationFlowModel works correctly
and coordinates the interactions between agents.
"""

import sys
import os
import mesa
import numpy as np
import matplotlib.pyplot as plt

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the model and agent classes
from infoflow.core.model import InformationFlowModel, create_model
from infoflow.agents.base import CitizenAgent, SocialMediaAgent
from infoflow.agents.media.corporate import CorporateMediaAgent
from infoflow.agents.media.influencer import InfluencerAgent
from infoflow.agents.media.government import GovernmentMediaAgent


def test_model_initialization(verbose=False):
    """Test that the model initializes correctly."""
    # Create a model with specific parameters
    model = InformationFlowModel(
        num_citizens=20,
        num_corporate_media=2,
        num_influencers=3,
        num_government=1,
        network_type="small_world",
        seed=42
    )
    
    # Set up connections
    model.setup_connections()
    
    # Check if agents were created
    if verbose:
        print(f"Model has {len(model.citizens)} citizen agents")
        print(f"Model has {len(model.corporate_medias)} corporate media agents")
        print(f"Model has {len(model.influencers)} influencer agents")
        print(f"Model has {len(model.government_medias)} government media agents")
    
    # Verify correct number of agents
    assert len(model.citizens) == 20
    assert len(model.corporate_medias) == 2
    assert len(model.influencers) == 3
    assert len(model.government_medias) == 1
    
    # Check network connections
    for citizen in model.citizens:
        # Each citizen should have neighbors in a small-world network
        if verbose and len(citizen.neighbors) > 0:
            print(f"Citizen {citizen.unique_id} has {len(citizen.neighbors)} neighbors")
            
        # In a small-world network, each node should have at least some neighbors
        # But this depends on the network parameters, so we don't assert a specific number
    
    # Check influencer followers
    total_followers = sum(len(inf.followers) for inf in model.influencers)
    if verbose:
        print(f"Influencers have {total_followers} total followers")
        
        # Show distribution of followers
        for i, inf in enumerate(model.influencers):
            print(f"Influencer {i+1} has {len(inf.followers)} followers")
    
    # At least some citizens should be followers
    assert total_followers > 0
    
    # Print initial truth assessment distribution
    if verbose:
        truth_assessments = [agent.truth_assessment for agent in model.citizens]
        print(f"Initial truth assessment mean: {np.mean(truth_assessments):.2f}")
        print(f"Initial truth assessment variance: {np.var(truth_assessments):.4f}")
    
    return model


def test_model_step(verbose=False):
    """Test that the model step function executes correctly."""
    model = create_model(
        num_citizens=30,
        num_corporate_media=2,
        num_influencers=3,
        num_government=1,
        network_type="small_world",
        seed=42
    )
    
    # Record initial state
    initial_truth_assessments = [agent.truth_assessment for agent in model.citizens]
    
    if verbose:
        print(f"Initial average truth assessment: {np.mean(initial_truth_assessments):.4f}")
        print(f"Initial truth assessment variance: {np.var(initial_truth_assessments):.4f}")
    
    # Run for several steps
    num_steps = 10
    for i in range(num_steps):
        model.step()
        
        if verbose and i % 3 == 0:
            current_truth_assessments = [agent.truth_assessment for agent in model.citizens]
            print(f"Step {i+1} - Avg truth assessment: {np.mean(current_truth_assessments):.4f}, " +
                  f"Variance: {np.var(current_truth_assessments):.4f}")
    
    # Check that truth assessments have changed
    final_truth_assessments = [agent.truth_assessment for agent in model.citizens]
    truth_assessment_changes = np.array(final_truth_assessments) - np.array(initial_truth_assessments)
    
    if verbose:
        print(f"\nFinal average truth assessment: {np.mean(final_truth_assessments):.4f}")
        print(f"Final truth assessment variance: {np.var(final_truth_assessments):.4f}")
        print(f"Average absolute truth assessment change: {np.mean(np.abs(truth_assessment_changes)):.4f}")
    
    # At least some truth assessments should have changed
    assert np.any(np.abs(truth_assessment_changes) > 0.01)
    
    return model


def test_data_collection(verbose=False):
    """Test that the model collects data properly."""
    model = create_model(
        num_citizens=30,
        num_corporate_media=2,
        num_influencers=3,
        num_government=1,
        network_type="small_world",
        seed=42
    )
    
    # Run for several steps
    num_steps = 10
    for i in range(num_steps):
        model.step()
    
    # Get collected data
    model_data = model.datacollector.get_model_vars_dataframe()
    agent_data = model.datacollector.get_agent_vars_dataframe()
    
    if verbose:
        print("Model-level data:")
        print(model_data.head())
        print("\nAgent-level data (first 5 rows):")
        print(agent_data.head())
        
        # Plot truth assessment over time
        plt.figure(figsize=(10, 6))
        plt.plot(model_data["Average Truth Assessment"])
        plt.title("Average Truth Assessment Over Time")
        plt.xlabel("Step")
        plt.ylabel("Average Truth Assessment")
        plt.ylim(0, 1)
        plt.grid(True)
        plt.show()
    
    # Check that we have the expected data
    assert "Average Truth Assessment" in model_data.columns
    assert "Truth Assessment Variance" in model_data.columns
    assert "Trust in Corporate Media" in model_data.columns
    assert len(model_data) == num_steps + 1  # Initial + one for each step
    
    # Check agent-level data
    assert "Truth Assessment" in agent_data.columns
    assert "Truth Seeking" in agent_data.columns
    assert "Confirmation Bias" in agent_data.columns
    
    return model, model_data, agent_data


if __name__ == "__main__":
    # Run tests with verbose output
    print("Testing model initialization...")
    model = test_model_initialization(verbose=True)
    
    print("\nTesting model step function...")
    model = test_model_step(verbose=True)
    
    print("\nTesting data collection...")
    model, model_data, agent_data = test_data_collection(verbose=True)
    
    print("\nAll tests completed successfully!")