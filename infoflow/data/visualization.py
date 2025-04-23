"""
Visualization utilities for InfoFlow social media simulation results.
"""

from typing import Any, Dict, List, Optional
import matplotlib
# Set the backend to a non-interactive one to avoid window creation issues
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap


def plot_truth_assessment_distribution(
    truth_assessments: List[float], title: str = "Truth Assessment Distribution"
):
    """
    Plot a histogram of truth assessments from the simulation.

    Args:
        truth_assessments: List of agent truth assessments (0-1 scale)
        title: Title for the plot
    """
    plt.figure(figsize=(10, 5))
    plt.hist(truth_assessments, bins=20, alpha=0.7, color="skyblue", edgecolor="black")
    plt.title(title)
    plt.xlabel("Truth Assessment Value (0-1)")
    plt.ylabel("Number of Social Media Users")
    plt.grid(alpha=0.3)
    plt.tight_layout()

    # Add mean and median lines
    if len(truth_assessments) > 0:  # Properly check if array has elements
        mean = np.mean(truth_assessments)
        median = np.median(truth_assessments)
        plt.axvline(
            mean,
            color="red",
            linestyle="dashed",
            linewidth=2,
            label=f"Mean: {mean:.2f}",
        )
        plt.axvline(
            median,
            color="green",
            linestyle="dashed",
            linewidth=2,
            label=f"Median: {median:.2f}",
        )
        plt.legend()

    return plt.gcf()


def plot_trust_levels(data: Dict[str, List[float]]):
    """
    Plot average trust levels for different source types over time.

    Args:
        data: Dictionary with time series data for trust levels
    """
    plt.figure(figsize=(12, 6))

    colors = {
        "trust_in_CorporateMediaAgent": "#1976D2",  # Blue
        "trust_in_InfluencerAgent": "#E64A19",      # Orange
        "trust_in_GovernmentMediaAgent": "#388E3C", # Green
    }
    
    labels = {
        "trust_in_CorporateMediaAgent": "Corporate Social Media Accounts",
        "trust_in_InfluencerAgent": "Social Media Influencers",
        "trust_in_GovernmentMediaAgent": "Government Social Media Accounts",
    }

    for source_type, values in data.items():
        if source_type.startswith("trust_in_"):
            color = colors.get(source_type, "gray")
            label = labels.get(source_type, source_type.replace("trust_in_", "").replace("Agent", ""))
            plt.plot(values, label=label, linewidth=2, color=color)

    plt.title("Trust in Social Media Sources Over Time")
    plt.xlabel("Time Steps")
    plt.ylabel("Average Trust Level (0-10)")
    plt.ylim(0, 10)  # Fixed scale for trust
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    return plt.gcf()


def plot_truth_assessment_evolution(data: Dict[str, List[float]]):
    """
    Plot the evolution of truth assessment metrics over time.

    Args:
        data: Dictionary with time series data for truth assessments
    """
    plt.figure(figsize=(12, 6))

    if "mean_truth_assessment" in data:
        plt.plot(
            data["mean_truth_assessment"],
            label="Mean Truth Assessment",
            linewidth=2,
            color="#1976D2",
        )

    if "truth_assessment_variance" in data:
        plt.plot(
            data["truth_assessment_variance"],
            label="Truth Assessment Variance",
            linewidth=2,
            color="#E64A19",
            linestyle="--",
        )

    plt.title("Truth Assessment Evolution Over Time")
    plt.xlabel("Time Steps")
    plt.ylabel("Value")
    plt.ylim(0, 1)  # Fixed scale for truth assessment
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    return plt.gcf()


def create_network_visualization(model, node_color_attribute: str = "truth_assessment"):
    """
    Create a visualization of the agent network.

    Args:
        model: The simulation model
        node_color_attribute: Agent attribute to use for node colors
    """
    try:
        import matplotlib.cm as cm
        import networkx as nx

        # Get the network from the model
        G = model.G.copy()

        # Get positions using a layout algorithm
        pos = nx.spring_layout(G, seed=42)  # Fixed seed for reproducibility

        plt.figure(figsize=(12, 12))

        # Get attribute values for coloring
        node_colors = []
        for i in range(len(G.nodes())):
            agent = model.grid.get_cell_list_contents([i])[0]
            value = getattr(
                agent, node_color_attribute, 0.5
            )  # Default 0.5 if attribute not found
            node_colors.append(value)

        # Draw nodes
        nodes = nx.draw_networkx_nodes(
            G, pos, node_color=node_colors, node_size=100, cmap=cm.viridis, alpha=0.8
        )

        # Draw edges
        nx.draw_networkx_edges(G, pos, alpha=0.2)

        # Add colorbar
        plt.colorbar(nodes, label=node_color_attribute.replace("_", " ").title())

        plt.title(f"Social Media User Network (colored by {node_color_attribute})")
        plt.axis("off")
        plt.tight_layout()

        return plt.gcf()
    except ImportError:
        print("NetworkX is required for network visualization")
        return None


def plot_trust_distribution(trust_levels: List[float], source_type: str):
    """
    Plot a histogram of trust levels for a specific source type.

    Args:
        trust_levels: List of agent trust levels (0-10 scale)
        source_type: Type of source (string label)
    """
    plt.figure(figsize=(10, 5))
    
    # Define bins and color gradient
    bins = np.linspace(0, 10, 21)
    cmap = plt.cm.RdYlGn
    
    # Create the histogram without specifying colors first
    n, bins, patches = plt.hist(trust_levels, bins=bins, alpha=0.8, edgecolor="black")
    
    # Colorize the patches based on bin position
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    # Normalize the bin centers to [0, 1]
    col = (bin_centers - min(bin_centers)) / (max(bin_centers) - min(bin_centers))
    
    # Apply colors to patches
    for c, p in zip(col, patches):
        plt.setp(p, 'facecolor', cmap(c))
    
    plt.title(f"Trust Distribution: {source_type}")
    plt.xlabel("Trust Level (0-10)")
    plt.ylabel("Number of Social Media Users")
    plt.xlim(0, 10)
    plt.grid(alpha=0.3)
    
    # Add mean and median lines
    if len(trust_levels) > 0:  # Properly check if array has elements
        mean = np.mean(trust_levels)
        median = np.median(trust_levels)
        plt.axvline(
            mean,
            color="red",
            linestyle="dashed",
            linewidth=2,
            label=f"Mean: {mean:.2f}",
        )
        plt.axvline(
            median,
            color="blue",
            linestyle="dashed",
            linewidth=2,
            label=f"Median: {median:.2f}",
        )
        plt.legend()
    
    plt.tight_layout()
    return plt.gcf()


def plot_cognitive_parameter_distribution(values: List[float], parameter_name: str, scale: tuple = (0, 10)):
    """
    Plot a histogram of cognitive parameter distribution.

    Args:
        values: List of parameter values
        parameter_name: Name of the parameter
        scale: Tuple of (min, max) values for the parameter
    """
    plt.figure(figsize=(10, 5))
    
    min_val, max_val = scale
    bins = np.linspace(min_val, max_val, 21)
    
    # Color map depends on parameter type
    if parameter_name.lower() == "truth_seeking":
        # For truth seeking (-5 to 5), use a diverging colormap
        cmap = LinearSegmentedColormap.from_list("truth_seeking", ["#E64A19", "#FFEB3B", "#1976D2"])
    else:
        # For other parameters (0-10), use a sequential colormap
        cmap = plt.cm.viridis
    
    # Plot histogram without specifying colors first
    n, bins, patches = plt.hist(values, bins=bins, alpha=0.8, edgecolor="black")
    
    # Colorize the patches based on bin position
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    # Normalize the bin centers to [0, 1]
    col = (bin_centers - min(bin_centers)) / (max(bin_centers) - min(bin_centers))
    
    # Apply colors to patches
    for c, p in zip(col, patches):
        plt.setp(p, 'facecolor', cmap(c))
    
    # Format parameter name for display
    display_name = parameter_name.replace("_", " ").title()
    
    plt.title(f"{display_name} Distribution")
    plt.xlabel(f"{display_name} Value {scale}")
    plt.ylabel("Number of Social Media Users")
    plt.xlim(min_val, max_val)
    plt.grid(alpha=0.3)
    
    # Add mean and median lines
    if len(values) > 0:  # Properly check if array has elements
        mean = np.mean(values)
        median = np.median(values)
        plt.axvline(
            mean,
            color="red",
            linestyle="dashed",
            linewidth=2,
            label=f"Mean: {mean:.2f}",
        )
        plt.axvline(
            median,
            color="blue",
            linestyle="dashed",
            linewidth=2,
            label=f"Median: {median:.2f}",
        )
        plt.legend()
    
    plt.tight_layout()
    return plt.gcf()


def plot_polarization_over_time(polarization_values: List[float]):
    """
    Plot polarization index over time.

    Args:
        polarization_values: List of polarization indices over time
    """
    plt.figure(figsize=(12, 6))
    
    plt.plot(polarization_values, linewidth=2, color="#673AB7")
    
    plt.title("Belief Polarization Over Time")
    plt.xlabel("Time Steps")
    plt.ylabel("Polarization Index")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    return plt.gcf()


def plot_opinion_clusters_over_time(cluster_counts: List[int]):
    """
    Plot the number of opinion clusters over time.

    Args:
        cluster_counts: List of opinion cluster counts over time
    """
    plt.figure(figsize=(12, 6))
    
    plt.plot(cluster_counts, linewidth=2, color="#FF5722", drawstyle="steps-post")
    
    plt.title("Opinion Clusters Over Time")
    plt.xlabel("Time Steps")
    plt.ylabel("Number of Distinct Opinion Clusters")
    plt.ylim(bottom=0)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    return plt.gcf()


def plot_parameter_vs_truth_assessment(parameter_values: List[float], 
                                       truth_assessments: List[float],
                                       parameter_name: str):
    """
    Create a scatter plot showing relationship between a parameter and truth assessment.

    Args:
        parameter_values: List of parameter values
        truth_assessments: List of corresponding truth assessments
        parameter_name: Name of the parameter
    """
    plt.figure(figsize=(10, 6))
    
    # Make sure we have data to plot
    if len(parameter_values) == 0 or len(truth_assessments) == 0:
        # Create empty plot with a message
        plt.text(0.5, 0.5, "No data available", 
                 horizontalalignment='center',
                 verticalalignment='center',
                 transform=plt.gca().transAxes)
        plt.title(f"Relationship Between {parameter_name.replace('_', ' ').title()} and Truth Assessment")
        plt.tight_layout()
        return plt.gcf()
    
    try:
        # Calculate correlation
        correlation = np.corrcoef(parameter_values, truth_assessments)[0, 1]
        
        # Create scatter plot
        plt.scatter(parameter_values, truth_assessments, alpha=0.6, c='#1976D2')
        
        # Add regression line - only if we have more than one point
        if len(parameter_values) > 1:
            z = np.polyfit(parameter_values, truth_assessments, 1)
            p = np.poly1d(z)
            
            # Use proper x values for the regression line
            x_range = np.linspace(min(parameter_values), max(parameter_values), 100)
            plt.plot(x_range, p(x_range), color='#E64A19', linestyle='--', linewidth=2)
        
        # Format parameter name for display
        display_name = parameter_name.replace("_", " ").title()
        
        plt.title(f"Relationship Between {display_name} and Truth Assessment")
        plt.xlabel(display_name)
        plt.ylabel("Truth Assessment")
        plt.grid(alpha=0.3)
        
        # Add annotation with correlation coefficient
        plt.annotate(f"Correlation: {correlation:.2f}", 
                     xy=(0.05, 0.95), 
                     xycoords='axes fraction',
                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
    except Exception as e:
        # If anything fails, create a simple error message
        plt.clf()  # Clear the figure
        plt.text(0.5, 0.5, f"Error creating plot: {str(e)}", 
                 horizontalalignment='center',
                 verticalalignment='center',
                 transform=plt.gca().transAxes)
        plt.title(f"Relationship Between {parameter_name.replace('_', ' ').title()} and Truth Assessment")
    
    plt.tight_layout()
    return plt.gcf()


def plot_content_sources(data: Dict[str, Any]):
    """
    Plot a pie chart showing the distribution of content by source type.
    
    Args:
        data: Dictionary with content data
    
    Returns:
        Matplotlib figure
    """
    plt.figure(figsize=(10, 7))
    
    # Check if we have content source data
    if "content_sources" in data and isinstance(data["content_sources"], dict) and data["content_sources"]:
        # Extract source types and counts
        source_types = list(data["content_sources"].keys())
        counts = list(data["content_sources"].values())
        
        # Use a categorical colormap
        colors = plt.cm.tab10.colors[:len(source_types)]
        
        # Create a pie chart
        wedges, texts, autotexts = plt.pie(
            counts, 
            labels=source_types, 
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            wedgeprops={'edgecolor': 'w', 'linewidth': 1}
        )
        
        # Customize text elements
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_color('white')
        
        plt.title("Content Distribution by Source Type")
        plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
        
    else:
        # Create a placeholder image
        plt.text(0.5, 0.5, "Content source data not available", 
                horizontalalignment='center',
                verticalalignment='center',
                transform=plt.gca().transAxes,
                fontsize=14)
        
        plt.text(0.5, 0.4, "This simulation may not track content source statistics",
                horizontalalignment='center', 
                verticalalignment='center',
                transform=plt.gca().transAxes, 
                fontsize=10)
        
        plt.title("Content Sources")
        plt.axis('off')
    
    plt.tight_layout()
    return plt.gcf()


def plot_content_spread(data: Dict[str, Any]):
    """
    Create a visualization of content spread through the network.
    
    Args:
        data: Dictionary with content spread data
    
    Returns:
        Matplotlib figure
    """
    plt.figure(figsize=(10, 7))
    
    # Check if we have content flow data
    if "content_flow_data" in data and isinstance(data["content_flow_data"], list) and data["content_flow_data"]:
        # Extract data for visualization
        spread_lengths = []
        for content in data["content_flow_data"]:
            if "spread_path" in content and isinstance(content["spread_path"], list):
                spread_lengths.append(len(content["spread_path"]))
        
        if spread_lengths:
            # Create histogram of spread path lengths
            bins = np.arange(1, max(spread_lengths) + 2) - 0.5
            plt.hist(spread_lengths, bins=bins, alpha=0.7, color="#1976D2", edgecolor="black")
            
            plt.xlabel("Number of Social Media Users Reached")
            plt.ylabel("Count of Content Items")
            plt.title("Content Spread Distribution")
            plt.grid(alpha=0.3)
            
            # Add average line
            avg_spread = np.mean(spread_lengths)
            plt.axvline(
                avg_spread,
                color="red",
                linestyle="dashed",
                linewidth=2,
                label=f"Avg. Reach: {avg_spread:.1f} users"
            )
            plt.legend()
            
            # Set x-ticks to be integers
            plt.xticks(range(1, max(spread_lengths) + 1))
        else:
            plt.text(0.5, 0.5, "No content spread data available", 
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=plt.gca().transAxes,
                    fontsize=14)
            plt.axis('off')
    else:
        # Create a placeholder image
        plt.text(0.5, 0.5, "Content spread data not available", 
                horizontalalignment='center',
                verticalalignment='center',
                transform=plt.gca().transAxes,
                fontsize=14)
        
        plt.text(0.5, 0.4, "This simulation may not track content flow through the network",
                horizontalalignment='center', 
                verticalalignment='center',
                transform=plt.gca().transAxes, 
                fontsize=10)
        
        plt.title("Content Spread")
        plt.axis('off')
    
    plt.tight_layout()
    return plt.gcf()


def create_complete_metrics_dashboard(data: Dict[str, Any], model=None):
    """
    Create a comprehensive dashboard with multiple visualizations.
    
    Args:
        data: Dictionary with metrics data
        model: Optional model instance for network visualization
    
    Returns:
        Dictionary of figure objects
    """
    figures = {}
    
    try:
        # Truth assessment visualizations
        if "current_truth_assessments" in data and len(data.get("current_truth_assessments", [])) > 0:
            figures["truth_distribution"] = plot_truth_assessment_distribution(
                data["current_truth_assessments"], "Current Truth Assessment Distribution"
            )
        
        if "mean_truth_assessment" in data and isinstance(data["mean_truth_assessment"], list) and len(data["mean_truth_assessment"]) > 0:
            figures["truth_evolution"] = plot_truth_assessment_evolution(data)
        
        # Trust level visualizations
        trust_data = {k: v for k, v in data.items() if k.startswith("trust_in_") and isinstance(v, list) and len(v) > 0}
        if trust_data:
            figures["trust_evolution"] = plot_trust_levels(trust_data)
        
        for source_type in ["CorporateMediaAgent", "InfluencerAgent", "GovernmentMediaAgent"]:
            key = f"current_trust_in_{source_type}"
            if key in data and len(data.get(key, [])) > 0:
                label = source_type.replace("Agent", " Social Media Accounts")
                if source_type == "InfluencerAgent":
                    label = "Social Media Influencers"
                figures[f"trust_dist_{source_type}"] = plot_trust_distribution(
                    data[key], label
                )
        
        # Cognitive parameter distributions
        for param in ["confirmation_bias", "critical_thinking", "social_conformity"]:
            key = f"current_{param}"
            if key in data and len(data.get(key, [])) > 0:
                figures[f"{param}_dist"] = plot_cognitive_parameter_distribution(
                    data[key], param
                )
        
        if "current_truth_seeking" in data and len(data.get("current_truth_seeking", [])) > 0:
            figures["truth_seeking_dist"] = plot_cognitive_parameter_distribution(
                data["current_truth_seeking"], "truth_seeking", (-5, 5)
            )
        
        # Polarization and clusters
        if "polarization_over_time" in data and len(data.get("polarization_over_time", [])) > 0:
            figures["polarization"] = plot_polarization_over_time(data["polarization_over_time"])
        
        if "opinion_clusters_over_time" in data and len(data.get("opinion_clusters_over_time", [])) > 0:
            figures["opinion_clusters"] = plot_opinion_clusters_over_time(data["opinion_clusters_over_time"])
        
        # Content metrics 
        figures["content_sources"] = plot_content_sources(data)
        figures["content_spread"] = plot_content_spread(data)
        
        # Parameter vs truth assessment relationships
        for param in ["confirmation_bias", "critical_thinking", "social_conformity", "truth_seeking"]:
            key = f"current_{param}"
            if (key in data and "current_truth_assessments" in data and 
                len(data.get(key, [])) > 0 and len(data.get("current_truth_assessments", [])) > 0):
                figures[f"{param}_vs_truth"] = plot_parameter_vs_truth_assessment(
                    data[key], data["current_truth_assessments"], param
                )
        
        # Network visualization if model is provided
        if model:
            try:
                figures["network_truth"] = create_network_visualization(model, "truth_assessment")
            except Exception as e:
                print(f"Error creating network visualization: {e}")
                # Create a placeholder figure instead
                fig = plt.figure(figsize=(10, 10))
                plt.text(0.5, 0.5, "Network visualization not available", 
                         horizontalalignment='center',
                         verticalalignment='center',
                         transform=plt.gca().transAxes)
                plt.title("Social Media User Network")
                figures["network_truth"] = fig
    
    except Exception as e:
        print(f"Error in create_complete_metrics_dashboard: {e}")
        # Create at least one placeholder figure if everything fails
        fig = plt.figure(figsize=(10, 5))
        plt.text(0.5, 0.5, f"Error creating dashboard: {str(e)}", 
                 horizontalalignment='center',
                 verticalalignment='center',
                 transform=plt.gca().transAxes)
        plt.title("Dashboard Error")
        figures["error"] = fig
    
    return figures