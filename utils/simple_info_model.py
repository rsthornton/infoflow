#!/usr/bin/env python3.11
"""
Simple example of running the InfoFlow model.

This script demonstrates how to create, configure, and run the InfoFlow model,
and how to access the collected data.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.models import create_model

def run_simple_simulation():
    """Run a simple simulation and visualize the results."""
    # Create a model with default parameters
    model = create_model(
        num_citizens=50,
        num_corporate_media=3,
        num_influencers=5,
        num_government=1,
        network_type="small_world",
        seed=42
    )
    
    print("Model initialized with:")
    print(f"  {len(model.citizens)} citizens")
    print(f"  {len(model.corporate_medias)} corporate media agents")
    print(f"  {len(model.influencers)} influencers")
    print(f"  {len(model.government_medias)} government media agents")
    
    # Run the simulation for 20 steps
    for i in range(20):
        model.step()
        if i % 5 == 0:
            print(f"Step {i+1} completed")
    
    print("Simulation completed")
    
    # Get the collected data
    model_data = model.datacollector.get_model_vars_dataframe()
    
    # Plot the average belief over time
    plt.figure(figsize=(10, 6))
    plt.plot(model_data["Average Belief"], linewidth=2)
    plt.title("Average Truth Assessment Over Time")
    plt.xlabel("Steps")
    plt.ylabel("Average Truth Assessment (0-1)")
    plt.ylim(0, 1)
    plt.grid(True)
    
    # Plot the trust levels over time
    plt.figure(figsize=(10, 6))
    plt.plot(model_data["Trust in Corporate Media"], label="Corporate Media", linewidth=2)
    plt.plot(model_data["Trust in Influencers"], label="Influencers", linewidth=2)
    plt.plot(model_data["Trust in Government"], label="Government", linewidth=2)
    plt.title("Trust Levels Over Time")
    plt.xlabel("Steps")
    plt.ylabel("Average Trust Level (0-10)")
    plt.ylim(0, 10)
    plt.legend()
    plt.grid(True)
    
    # Plot the belief variance over time
    plt.figure(figsize=(10, 6))
    plt.plot(model_data["Belief Variance"], linewidth=2)
    plt.title("Truth Assessment Variance Over Time")
    plt.xlabel("Steps")
    plt.ylabel("Variance")
    plt.grid(True)
    
    plt.show()
    
    return model, model_data

if __name__ == "__main__":
    model, data = run_simple_simulation()
    
    # Print some statistics
    print("\nFinal statistics:")
    print(f"  Average truth assessment: {data['Average Belief'].iloc[-1]:.4f}")
    print(f"  Truth assessment variance: {data['Belief Variance'].iloc[-1]:.4f}")
    print(f"  Trust in corporate media: {data['Trust in Corporate Media'].iloc[-1]:.2f}")
    print(f"  Trust in influencers: {data['Trust in Influencers'].iloc[-1]:.2f}")
    print(f"  Trust in government: {data['Trust in Government'].iloc[-1]:.2f}")