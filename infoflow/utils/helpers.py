"""
Helper functions for InfoFlow simulation.
"""


def calculate_variance(values):
    """
    Calculate variance of a list of values.

    Args:
        values: List of numerical values

    Returns:
        The variance of the values
    """
    if not values:
        return 0

    mean = sum(values) / len(values)
    return sum((x - mean) ** 2 for x in values) / len(values)
