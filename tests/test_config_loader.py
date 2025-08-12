import pytest
from utils.config_loader import ConfigLoader
from box import Box
from pathlib import Path

def test_config_loader_loads_valid_config(tmp_path):
    config_content = """
input:
  data_file: "data.csv"
  group_col: "group"
  value_col: "value"
  lower_limit_col: "lower"
  upper_limit_col: "upper"
analyses:
  - name: "AnovaAnalysis"
plots:
  - name: "BoxPlot"
output: "output"
report:
  name: "test_report"
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    loader = ConfigLoader(str(config_file))
    assert isinstance(loader.settings, Box)
    assert loader.settings.input.group_col == "group"

def test_config_loader_raises_error_on_missing_key(tmp_path):
    # Create a minimal default_config.yaml that is missing lower_limit_col
    default_config_content = """
input:
  data_file: "data.csv"
  group_col: "group"
  value_col: "value"
  upper_limit_col: "upper"
analyses: []
plots: []
output:
  output_directory: "output"
  save_interactive_html: false
  save_static_html: false
  save_pdf: false
report:
  name: "default_report"
"""
    default_config_file = tmp_path / "default_config.yaml"
    default_config_file.write_text(default_config_content)

    # Create a config.yaml that is also missing lower_limit_col
    config_content = """
input:
  group_col: "group"
  value_col: "value"
  upper_limit_col: "upper"
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)

    with pytest.raises(KeyError, match="Missing key in input section: lower_limit_col"):
        ConfigLoader(str(config_file), default_config_file=str(default_config_file))
