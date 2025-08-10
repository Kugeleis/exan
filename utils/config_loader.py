from pathlib import Path
from box import Box
import importlib
import pkgutil
from utils.analysis_registry import ANALYSIS_REGISTRY
from utils.plot_registry import PLOT_REGISTRY

class ConfigLoader:
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = Path(config_file)
        self._config: Box = self._load()
        self._validate()
        self._autoimport('utils.analyses')
        self._autoimport('utils.plots')

    def _load(self) -> Box:
        return Box().from_yaml(filename=self.config_file)

    def _validate(self):
        for key in ["group_col","value_col","lower_limit_col","upper_limit_col","analyses","plots","output"]:
            if key not in self._config:
                raise KeyError(f"Missing key: {key}")

    def _autoimport(self, pkg):
        package = importlib.import_module(pkg)
        path = Path(__file__).parent / "utils"
        for _, modname, ispkg in pkgutil.iter_modules([str(path)]):
            if not ispkg:
                importlib.import_module(f"{pkg}.{modname}")

    @property
    def settings(self): return self._config
    def get_analysis_instance(self, name): return ANALYSIS_REGISTRY[name]()
    def get_plot_instance(self, name): return PLOT_REGISTRY[name]()
