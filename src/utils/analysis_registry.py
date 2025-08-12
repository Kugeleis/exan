"""
analysis_registry.py

This module provides a registry for statistical analysis classes.
Analysis classes can be registered using the `register_analysis` decorator,
making them discoverable and instantiable by their names.
"""

# A dictionary to store registered analysis classes, keyed by their names.
ANALYSIS_REGISTRY = {}

def register_analysis(cls):
    """
    Decorator to register an analysis class in the ANALYSIS_REGISTRY.

    The class name is used as the key in the registry. Only classes ending with
    "Analysis" are registered.

    Args:
        cls (type): The analysis class to register.

    Returns:
        type: The registered class (unmodified).
    """
    name = cls.__name__
    if name.endswith("Analysis"):
        ANALYSIS_REGISTRY[name] = cls
    return cls