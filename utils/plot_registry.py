"""
plot_registry.py

This module provides a registry for plot classes.
Plot classes can be registered using the `register_plot` decorator,
making them discoverable and instantiable by their names.
"""

# A dictionary to store registered plot classes, keyed by their names.
PLOT_REGISTRY = {}

def register_plot(cls):
    """
    Decorator to register a plot class in the PLOT_REGISTRY.

    The class name is used as the key in the registry. Only classes ending with
    "Plot" are registered.

    Args:
        cls (type): The plot class to register.

    Returns:
        type: The registered class (unmodified).
    """
    name = cls.__name__
    if name.endswith("Plot"):
        PLOT_REGISTRY[name] = cls
    return cls