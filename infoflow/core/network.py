"""
Network utilities for InfoFlow simulation.

This module provides helper functions for creating different types of
social networks for the InfoFlow simulation.
"""

from typing import Any, Dict, Optional

import networkx as nx


def create_small_world_network(
    num_nodes: int, k: int = 4, p: float = 0.1, seed: Optional[int] = None
) -> nx.Graph:
    """
    Create a small-world network using the Watts-Strogatz model.

    Args:
        num_nodes: Number of nodes in the network
        k: Each node is connected to k nearest neighbors
        p: Probability of rewiring each edge
        seed: Random seed for reproducibility

    Returns:
        A networkx graph representing a small-world network
    """
    # Safety check: k must be less than num_nodes and even
    if num_nodes <= k:
        # If we have too few nodes, fall back to a complete graph
        return nx.complete_graph(num_nodes)
    
    # k must be even for watts_strogatz_graph
    if k % 2 == 1:
        k = max(2, k - 1)  # Ensure k is even and at least 2
        
    return nx.watts_strogatz_graph(n=num_nodes, k=k, p=p, seed=seed)


def create_scale_free_network(
    num_nodes: int, m: int = 3, seed: Optional[int] = None
) -> nx.Graph:
    """
    Create a scale-free network using the Barabasi-Albert model.

    Args:
        num_nodes: Number of nodes in the network
        m: Number of edges to attach from a new node to existing nodes
        seed: Random seed for reproducibility

    Returns:
        A networkx graph representing a scale-free network
    """
    # Safety check: Barabasi-Albert requires m < num_nodes
    if num_nodes <= m:
        # If we have too few nodes, fall back to a complete graph
        return nx.complete_graph(num_nodes)
    
    # For very small networks, we need to adjust m
    if num_nodes < 5 and m > 1:
        m = 1  # For very small networks, use minimal connections
        
    return nx.barabasi_albert_graph(n=num_nodes, m=m, seed=seed)


def create_random_network(
    num_nodes: int, p: float = 0.1, seed: Optional[int] = None
) -> nx.Graph:
    """
    Create a random network using the Erdos-Renyi model.

    Args:
        num_nodes: Number of nodes in the network
        p: Probability of edge creation
        seed: Random seed for reproducibility

    Returns:
        A networkx graph representing a random network
    """
    return nx.erdos_renyi_graph(n=num_nodes, p=p, seed=seed)


def create_network(
    network_type: str,
    num_nodes: int,
    params: Dict[str, Any],
    seed: Optional[int] = None,
) -> nx.Graph:
    """
    Create a network of the specified type.

    Args:
        network_type: Type of network to create ("small_world", "scale_free", "random")
        num_nodes: Number of nodes in the network
        params: Parameters for network creation
        seed: Random seed for reproducibility

    Returns:
        A networkx graph object of the specified type
    """
    # Safety check: For very small networks, default to complete graph
    if num_nodes <= 3:
        print(f"Network too small (n={num_nodes}), using complete graph instead")
        return nx.complete_graph(num_nodes)
        
    if network_type == "small_world":
        return create_small_world_network(
            num_nodes=num_nodes,
            k=params.get("small_world_k", 4),
            p=params.get("small_world_p", 0.1),
            seed=seed,
        )
    elif network_type == "scale_free":
        return create_scale_free_network(
            num_nodes=num_nodes, m=params.get("scale_free_m", 3), seed=seed
        )
    elif network_type == "random":
        return create_random_network(
            num_nodes=num_nodes, p=params.get("random_p", 0.1), seed=seed
        )
    else:
        # Default to a complete graph (everyone connected)
        return nx.complete_graph(num_nodes)
