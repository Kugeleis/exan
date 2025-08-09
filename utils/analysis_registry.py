# analysis_registry.py
ANALYSIS_REGISTRY = {}

def register_analysis(cls):
    name = cls.__name__
    if name.endswith("Analysis"):
        ANALYSIS_REGISTRY[name] = cls
    return cls
