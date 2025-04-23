"""
Tests for the base agent classes in InfoFlow.

This module contains tests to verify that the base agent functionality 
is working correctly with Mesa 3.
"""

import sys
import os
import mesa
import numpy as np

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the base agent classes
from infoflow.agents.base import BaseAgent, CitizenAgent, SocialMediaAgent


class SimpleTestModel(mesa.Model):
    """A simple model for testing agent functionality."""
    
    def __init__(self, num_citizens=10, num_media=3, seed=None):
        """Initialize the test model.
        
        Args:
            num_citizens: Number of citizen agents
            num_media: Number of social media agents
            seed: Random seed for reproducibility
        """
        super().__init__(seed=seed)
        
        # Create citizen agents with different values
        for i in range(num_citizens):
            truth_seeking = i % 5 - 2  # Values from -2 to 2
            CitizenAgent(
                model=self,
                truth_seeking=truth_seeking
            )
        
        # Create social media agents
        for i in range(num_media):
            bias = (i % 3 - 1) * 3  # Values -3, 0, 3
            SocialMediaAgent(
                model=self,
                political_bias=bias
            )
        
        # Get references to the agents by type
        from mesa.agent import AgentSet
        # Filter agents by type using a list comprehension and pass the random generator
        self.citizens = AgentSet(
            [a for a in self.agents if isinstance(a, CitizenAgent)],
            random=self.random  # Pass the model's random generator for reproducibility
        )
        self.media_agents = AgentSet(
            [a for a in self.agents if isinstance(a, SocialMediaAgent)],
            random=self.random  # Pass the model's random generator for reproducibility
        )
        
        # Set up a simple network (each citizen connects to two others)
        for i, citizen in enumerate(self.citizens):
            # Connect to the next two citizens (with wraparound)
            next_idx = (i + 1) % len(self.citizens)
            next_next_idx = (i + 2) % len(self.citizens)
            citizen.neighbors = [
                self.citizens[next_idx],
                self.citizens[next_next_idx]
            ]
    
    def step(self):
        """Advance the model by one step."""
        # Step all agents using Mesa 3 AgentSet methods
        # Step all citizen agents first
        self.citizens.do("step")
        
        # Then step all media agents
        self.media_agents.do("step")


def test_agent_initialization(verbose=False):
    """Test that agents initialize correctly with Mesa 3."""
    model = SimpleTestModel(seed=42)
    
    # Check if unique_ids are assigned automatically
    assert len(model.citizens) == 10
    assert len(model.media_agents) == 3
    
    if verbose:
        print(f"   Created model with {len(model.citizens)} citizens and {len(model.media_agents)} media agents")
        print(f"   Total agents in model: {len(model.agents)}")
    
    # Check that all agents have unique IDs
    all_ids = [agent.unique_id for agent in model.agents]
    assert len(all_ids) == len(set(all_ids))  # No duplicate IDs
    
    if verbose:
        print(f"   All agents have unique IDs: {sorted(all_ids)}")
    
    # Verify agent attributes
    for i, citizen in enumerate(model.citizens):
        assert 0 <= citizen.truth_assessment <= 1
        assert -5 <= citizen.truth_seeking <= 5
        assert len(citizen.neighbors) == 2
        
        if verbose and i < 3:  # Show first 3 citizens
            print(f"   Citizen {citizen.unique_id}: truth_assessment={citizen.truth_assessment:.2f}, truth_seeking={citizen.truth_seeking}")
            print(f"     Connected to citizens: {[n.unique_id for n in citizen.neighbors]}")
    
    for i, media in enumerate(model.media_agents):
        assert -5 <= media.political_bias <= 5
        assert 0 <= media.credibility <= 10
        assert 0 <= media.influence_reach <= 1
        
        if verbose:
            print(f"   Media {media.unique_id}: bias={media.political_bias}, credibility={media.credibility:.1f}")
    
    return model


def test_content_creation(verbose=False):
    """Test content creation by social media agents."""
    model = SimpleTestModel(seed=42)
    
    # Test content creation from each media agent
    for i, media_agent in enumerate(model.media_agents):
        content = media_agent.create_content()
        
        # Verify content structure
        assert "accuracy" in content
        assert "framing_bias" in content
        assert "source_authority" in content
        assert "source_credibility" in content
        assert "source_type" in content
        
        # Verify value ranges
        assert 0 <= content["accuracy"] <= 1
        assert -5 <= content["framing_bias"] <= 5  # Political bias scale from -5 to 5 (anti-Trump to pro-Trump)
        assert 0 <= content["source_authority"] <= 1
        assert 0 <= content["source_credibility"] <= 1
        
        if verbose:
            print(f"   Media {media_agent.unique_id} created content:")
            print(f"     - Accuracy: {content['accuracy']:.2f}")
            print(f"     - Framing bias: {content['framing_bias']:.2f}")
            print(f"     - Authority: {content['source_authority']:.2f}")
            print(f"     - Credibility: {content['source_credibility']:.2f}")
            print(f"     - Source type: {content['source_type']}")


def test_agent_step(verbose=False):
    """Test that agent step methods execute without errors."""
    model = SimpleTestModel(seed=42)
    
    if verbose:
        print(f"   Initial model step count: {model.steps}")
        # Show initial truth assessments of a few citizens
        print("   Initial citizen truth assessments:")
        for i, citizen in enumerate(model.citizens):
            if i < 3:  # First 3 citizens
                print(f"     Citizen {citizen.unique_id}: truth_assessment={citizen.truth_assessment:.2f}")
    
    # Run the model for a few steps
    for step in range(3):
        if verbose:
            print(f"   Running step {step+1}...")
        model.step()
    
    # Verify step count increased
    assert model.steps == 3
    
    if verbose:
        print(f"   Final model step count: {model.steps}")
        # Show final truth assessments of a few citizens
        print("   Final citizen truth assessments:")
        for i, citizen in enumerate(model.citizens):
            if i < 3:  # First 3 citizens
                print(f"     Citizen {citizen.unique_id}: truth_assessment={citizen.truth_assessment:.2f}")


def test_information_flow(verbose=False):
    """Test basic information flow between agents."""
    model = SimpleTestModel(seed=42)
    
    # Create test content
    test_content = {
        "accuracy": 0.8,
        "framing_bias": 0.2,
        "source_authority": 0.7,
        "source_credibility": 0.9,
        "source_type": "TestSource"
    }
    
    # Send content to a citizen
    citizen = model.citizens[0]
    media = model.media_agents[0]
    
    if verbose:
        print(f"   Sending test content from Media {media.unique_id} to Citizen {citizen.unique_id}")
        print(f"   Content: {test_content}")
        print(f"   Citizen memory before: {len(citizen.content_memory)} items")
    
    # Process content
    result = citizen.receive_information(test_content, media)
    
    # Verify content was stored in memory
    assert len(citizen.content_memory) == 1
    assert citizen.content_memory[0]["content"] == test_content
    assert citizen.content_memory[0]["source"] == media
    
    if verbose:
        print(f"   Content successfully received: {result}")
        print(f"   Citizen memory after: {len(citizen.content_memory)} items")
        print(f"   Memory contains content with accuracy: {citizen.content_memory[0]['content']['accuracy']}")
        print(f"   From source: {citizen.content_memory[0]['source'].unique_id}")


def test_memory_limit(verbose=False):
    """Test that content memory has a limit."""
    model = SimpleTestModel(seed=42)
    citizen = model.citizens[0]
    media = model.media_agents[0]
    
    if verbose:
        print(f"   Testing memory limit for Citizen {citizen.unique_id}")
        print(f"   Initial memory size: {len(citizen.content_memory)}")
    
    # Add more than the limit of items to memory
    for i in range(15):
        test_content = {"accuracy": 0.5, "test_id": i}
        citizen.receive_information(test_content, media)
        
        if verbose and (i == 0 or i == 9 or i == 14):
            print(f"   After adding item {i}, memory size: {len(citizen.content_memory)}")
    
    # Check that only the most recent are kept
    assert len(citizen.content_memory) == 10
    assert citizen.content_memory[0]["content"]["test_id"] == 5
    assert citizen.content_memory[-1]["content"]["test_id"] == 14
    
    if verbose:
        print(f"   Final memory size: {len(citizen.content_memory)} (limited to 10)")
        print(f"   First item test_id: {citizen.content_memory[0]['content']['test_id']} (should be 5)")
        print(f"   Last item test_id: {citizen.content_memory[-1]['content']['test_id']} (should be 14)")


if __name__ == "__main__":
    # Run tests
    print("Testing agent initialization...")
    test_agent_initialization()
    
    print("Testing content creation...")
    test_content_creation()
    
    print("Testing agent step...")
    test_agent_step()
    
    print("Testing information flow...")
    test_information_flow()
    
    print("Testing memory limit...")
    test_memory_limit()
    
    print("All tests passed!")