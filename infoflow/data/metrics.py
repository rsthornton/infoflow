"""
Metric definitions for InfoFlow simulation.
"""

from typing import Any, Dict, List

import numpy as np


def calculate_polarization(truth_assessments: List[float]) -> float:
    """
    Calculate polarization index based on truth assessment distribution.

    Higher values indicate stronger polarization in how agents assess truthfulness.

    Args:
        truth_assessments: List of agent truth assessments (0-1 scale)

    Returns:
        Polarization index
    """
    # Simple implementation - can be enhanced
    sorted_assessments = sorted(truth_assessments)
    n = len(sorted_assessments)

    if n <= 1:
        return 0.0

    # Calculate average difference between consecutive truth assessments
    diffs = [sorted_assessments[i + 1] - sorted_assessments[i] for i in range(n - 1)]

    # Larger gaps suggest polarization
    return sum(diffs) / (n - 1)


def calculate_opinion_clusters(
    truth_assessments: List[float], threshold: float = 0.1
) -> int:
    """
    Calculate the number of opinion clusters in the population.

    Args:
        truth_assessments: List of agent truth assessments (0-1 scale)
        threshold: Minimum gap between clusters

    Returns:
        Number of distinct opinion clusters
    """
    if not truth_assessments:
        return 0

    sorted_assessments = sorted(truth_assessments)
    n = len(sorted_assessments)

    # Start with one cluster
    clusters = 1

    # Check for gaps between consecutive sorted assessments
    for i in range(n - 1):
        if sorted_assessments[i + 1] - sorted_assessments[i] > threshold:
            clusters += 1

    return clusters


def calculate_truth_correlation(
    truth_assessments: List[float], actual_truths: List[float]
) -> float:
    """
    Calculate correlation between agent truth assessments and actual truth values.

    Args:
        truth_assessments: List of agent truth assessments (0-1 scale)
        actual_truths: List of actual truth values (0-1 scale)

    Returns:
        Correlation coefficient
    """
    if len(truth_assessments) != len(actual_truths) or len(truth_assessments) == 0:
        return 0.0

    # Calculate means
    mean_assessment = sum(truth_assessments) / len(truth_assessments)
    mean_truth = sum(actual_truths) / len(actual_truths)

    # Calculate covariance and variances
    covariance = sum(
        (a - mean_assessment) * (t - mean_truth)
        for a, t in zip(truth_assessments, actual_truths)
    )
    var_assessment = sum((a - mean_assessment) ** 2 for a in truth_assessments)
    var_truth = sum((t - mean_truth) ** 2 for t in actual_truths)

    # Avoid division by zero
    if var_assessment == 0 or var_truth == 0:
        return 0.0

    return covariance / (np.sqrt(var_assessment) * np.sqrt(var_truth))
