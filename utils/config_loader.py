from pathlib import Path
import importlib
import pkgutil
from box import Box
from .analysis_registry import ANALYSIS_REGISTRY
from .plot_registry import PLOT_REGISTRY
from .types_custom import Config

class ConfigLoader:
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = Path(config_file)
        self._config: Config = Box.from_yaml(filename=self.config_file)
        self._validate()
        self._autoimport('utils.analyses')
        self._autoimport('utils.plots')

    def _validate(self):
        # This validation is now largely handled by the TypedDict, but basic key presence can remain
        for key in ["group_col","value_col","lower_limit_col","upper_limit_col","analyses","plots","output", "report"]:
            if key not in self._config:
                raise KeyError(f"Missing key: {key}")
        if "name" not in self._config["report"]:
            raise KeyError("Missing key: name in report section")

    def _autoimport(self, pkg):
        package = importlib.import_module(pkg)
        path = Path(__file__).parent / "utils"
        for _, modname, ispkg in pkgutil.iter_modules([str(path)]):
            if not ispkg:
                importlib.import_module(f".{modname}", __package__)

    @property
    def settings(self) -> Config: return self._config
    def get_analysis_instance(self, name): return ANALYSIS_REGISTRY[name]()
    def get_plot_instance(self, name): return PLOT_REGISTRY[name]()