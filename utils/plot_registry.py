# plot_registry.py
PLOT_REGISTRY = {}

def register_plot(cls):
    name = cls.__name__
    if name.endswith("Plot"):
        PLOT_REGISTRY[name] = cls
    return cls
