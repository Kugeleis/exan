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

### Style Configuration (`style.yaml`)

The `style.yaml` file is mandatory and defines the visual styling for various plot elements. It must be present in the root directory of the project.

Here is an example `style.yaml` configuration:

```yaml
limits_style:
  LSL:
    annotation_text: "LSL"
    line_color: "red"
    annotation_position_horizontal: "right"
    annotation_xshift_horizontal: 10
    annotation_position_vertical: "top"
    annotation_yshift_vertical: 10
  USL:
    annotation_text: "USL"
    line_color: "red"
    annotation_position_horizontal: "right"
    annotation_xshift_horizontal: 10
    annotation_position_vertical: "top"
    annotation_yshift_vertical: 10
  T:
    annotation_text: "T"
    line_color: "green"
    annotation_position_horizontal: "right"
    annotation_xshift_horizontal: 10
    annotation_position_vertical: "top"
    annotation_yshift_vertical: 10

axis:
  font_size: 12
  font_color: "black"
  title_font_size: 14
  title_font_color: "gray"
  show_grid: true
  grid_color: "lightgray"
  zero_line: true
  zero_line_color: "black"
```

*   `limits_style`: Defines the styling for limit lines (LSL, USL, Target).
    *   Each limit (LSL, USL, T) can have specific `annotation_text`, `line_color`, and positioning for both horizontal and vertical lines.
*   `axis`: Defines common styling properties for plot axes.
    *   `font_size`, `font_color`: For tick labels.
    *   `title_font_size`, `title_font_color`: For axis titles.
    *   `show_grid`, `grid_color`: For grid lines.
    *   `zero_line`, `zero_line_color`: For the zero axis line.

## Extending the Tool

### Adding a new Analysis

1.  Create a new class that inherits from `Analysis` in `utils/analyses.py`.
2.  Implement the `analyze` method.
3.  Add the `@register_analysis` decorator to your class.

### Adding a new Plot

1.  Create a new class that inherits from `Plot` in `utils/plots.py`.
2.  Implement the `plot` method.
3.  Add the `@register_plot` decorator to your class.