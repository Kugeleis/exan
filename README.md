# Exan - Data Analysis Tool

Exan is a configurable data analysis tool that allows you to run various statistical analyses and generate plots from your data. It is designed to be easily extensible, allowing you to add your own custom analyses and plots.

## Features

*   **Configurable Analysis Pipeline**: Define your analysis pipeline in a simple YAML file (`config.yaml`).
*   **Extensible**: Easily add your own analysis functions and plots.
*   **Multiple Analyses**: Comes with built-in support for ANOVA, T-Test, and Mann-Whitney U-Test.
*   **Multiple Plots**: Comes with built-in support for Box Plots and Cumulative Frequency Plots.
*   **Data Preprocessing**: Supports data preprocessing steps like outlier filtering.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/exan.git
    cd exan
    ```

2.  Install the dependencies using `uv`:
    ```bash
    uv venv
    ```

## Usage

1.  Configure your analysis in the `config.yaml` file. See the [Configuration](#configuration) section for more details.
2.  Make sure your data file is in the `data` directory. The default data file is `data/fake.csv`.
3.  Run the analysis:
    ```bash
    uv run main.py
    ```
4.  The analysis results will be printed to the console, and the plots will be saved as HTML files in the root directory.

## Configuration

The analysis pipeline is configured in the `config.yaml` file. Here is an example configuration:

```yaml
group_col: Group
value_col: Value
lower_limit_col: Lower_Limit
upper_limit_col: Upper_Limit

analyses:
  - name: AnovaAnalysis
    relevance: true
    relevance_threshold: 0.25
  - name: TTestAnalysis
  - name: MannWhitneyAnalysis

plots:
  - name: BoxPlot
  - name: CumulativeFrequencyPlot

output:
  width: 800
  height: 600
```

*   `group_col`: The name of the column that contains the groups to compare.
*   `value_col`: The name of the column that contains the values to analyze.
*   `lower_limit_col`: The name of the column that contains the lower limit for the relevance check.
*   `upper_limit_col`: The name of the column that contains the upper limit for the relevance check.
*   `analyses`: A list of analyses to perform. Each analysis is a dictionary with a `name` key. You can also provide a `relevance` key to enable the relevance check, and a `relevance_threshold` key to set the threshold for the relevance check.
*   `plots`: A list of plots to generate. Each plot is a dictionary with a `name` key.
*   `output`: A dictionary with output options, such as the width and height of the plots.

## Extending the Tool

### Adding a new Analysis

1.  Create a new class that inherits from `Analysis` in `utils/analyses.py`.
2.  Implement the `analyze` method.
3.  Add the `@register_analysis` decorator to your class.

### Adding a new Plot

1.  Create a new class that inherits from `Plot` in `utils/plots.py`.
2.  Implement the `plot` method.
3.  Add the `@register_plot` decorator to your class.
