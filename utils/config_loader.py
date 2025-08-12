from pathlib import Path
import importlib
import pkgutil
from box import Box
from .analysis_registry import ANALYSIS_REGISTRY
from .plot_registry import PLOT_REGISTRY
from .types_custom import Config

class ConfigLoader:
    """
    Loads and manages application configuration from YAML files.

    This class is responsible for loading the main configuration (`config.yaml`)
    and the style configuration (`style.yaml`). It also performs basic validation
    and auto-imports analysis and plot modules to register them.
    """
    def __init__(self, config_file: str = "config.yaml", style_file: str = "style.yaml", default_config_file: str = "default_config.yaml"):
        """
        Initializes the ConfigLoader by loading configuration files.

        Args:
            config_file (str): The path to the main configuration YAML file.
            style_file (str): The path to the style configuration YAML file.
            default_config_file (str): The path to the default configuration YAML file.
        
        Raises:
            FileNotFoundError: If the default_config_file does not exist, or if the style_file does not exist.
            KeyError: If essential keys are missing from the merged configuration.
        """
        self.default_config_file: str = default_config_file
        self.config_file = Path(config_file)
        self.style_file = Path(style_file)

        # Load default config
        self._config: Config = Box.from_yaml(filename=self.default_config_file)

        # Load user config and merge it into the default config
        if self.config_file.exists():
            user_config = Box.from_yaml(filename=self.config_file)
            self._config.merge_update(user_config)

        self._style_config: Box = Box.from_yaml(filename=self.style_file)
        self._validate()
        self._autoimport('utils.analyses')
        self._autoimport('utils.plots')

    def _validate(self):
        """
        Performs basic validation of the loaded configuration.

        Raises:
            KeyError: If essential keys are missing from the main configuration.
        """
        # Validate keys under 'input'
        for key in ["group_col", "value_col", "lower_limit_col", "upper_limit_col"]:
            if key not in self._config.input or self._config.input[key] is None:
                raise KeyError(f"Missing key in input section: {key}")

        # Validate top-level keys
        for key in ["analyses", "plots", "output", "report"]:
            if key not in self._config:
                raise KeyError(f"Missing key: {key}")

        if "name" not in self._config["report"]:
            raise KeyError("Missing key: name in report section")

    def _autoimport(self, pkg):
        """
        Automatically imports modules within a specified package to trigger registration decorators.

        Args:
            pkg (str): The name of the package to auto-import (e.g., 'utils.analyses').
        """
        package = importlib.import_module(pkg)
        path = Path(__file__).parent / "utils"
        for _, modname, ispkg in pkgutil.iter_modules([str(path)]):
            if not ispkg:
                importlib.import_module(f".{modname}", __package__)

    @property
    def settings(self) -> Config:
        """
        Returns the main application settings.

        Returns:
            Config: The main configuration object.
        """
        return self._config

    @property
    def style_settings(self) -> Box:
        """
        Returns the loaded style settings.

        Returns:
            Box: The style configuration object.
        """
        return self._style_config

    def get_analysis_instance(self, name):
        """
        Retrieves an instance of a registered analysis class.

        Args:
            name (str): The name of the analysis class to retrieve.

        Returns:
            Analysis: An instance of the requested analysis class.
        
        Raises:
            KeyError: If the analysis name is not registered.
        """
        return ANALYSIS_REGISTRY[name]()

    def get_plot_instance(self, name):
        """
        Retrieves an instance of a registered plot class.

        Args:
            name (str): The name of the plot class to retrieve.

        Returns:
            Plot: An instance of the requested plot class.
        
        Raises:
            KeyError: If the plot name is not registered.
        """
        return PLOT_REGISTRY[name]()
