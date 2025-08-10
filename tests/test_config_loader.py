import pytest
from utils.config_loader import ConfigLoader
from box import Box
from pathlib import Path

def test_config_loader_loads_valid_config(tmp_path):
    config_content = """
group_col: "group"
value_col: "value"
lower_limit_col: "lower"
upper_limit_col: "upper"
analyses:
  - name: "AnovaAnalysis"
plots:
  - name: "BoxPlot"
output: "output"
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    loader = ConfigLoader(str(config_file))
    assert isinstance(loader.settings, Box)
    assert loader.settings.group_col == "group"

def test_config_loader_raises_error_on_missing_key(tmp_path):
    config_content = """
group_col: "group"
value_col: "value"
# lower_limit_col is missing
upper_limit_col: "upper"
analyses:
  - name: "AnovaAnalysis"
plots:
  - name: "BoxPlot"
output: "output"
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    with pytest.raises(KeyError, match="Missing key: lower_limit_col"):
        ConfigLoader(str(config_file))
