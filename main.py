from utils.config_loader import ConfigLoader
import logging
import pandas as pd
from utils.relevance_decorator import relevance_decorator
from utils.analyses import AnovaAnalysis, TTestAnalysis, MannWhitneyAnalysis
from utils.reporting import generate_report
from utils.preprocessing import load_data_with_limits
from typing import List, Dict
from plotly.subplots import make_subplots
import plotly.graph_objects as go

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def process_columns(df: pd.DataFrame, config: Dict, limits: Dict) -> (Dict, List[Dict]):
    """
    Process each value column in the DataFrame, performing analyses and generating plots.

    :param df: The input DataFrame.
    :param config: The configuration dictionary.
    :param limits: A dictionary of limits.
    :return: A tuple containing a dictionary of generated plots and a list of analysis results.
    """
    group_col = config.group_col
    value_cols = [col for col in df.columns if col != group_col]
    plots = {}
    results = []

    for value_col in value_cols:
        logging.info(f"Processing column: {value_col}")

        lower_limit = limits.get(f"{value_col}_Lower_Limit")
        upper_limit = limits.get(f"{value_col}_Upper_Limit")

        num_groups = df[group_col].nunique()
        analyses_to_run = []
        if num_groups == 2:
            analyses_to_run = [TTestAnalysis, MannWhitneyAnalysis]
        elif num_groups > 2:
            analyses_to_run = [AnovaAnalysis]

        apply_relevance = any(analysis_cfg.get("relevance", False) for analysis_cfg in config.analyses)
        relevance_threshold = next((analysis_cfg.get("relevance_threshold", 0.2) for analysis_cfg in config.analyses if "relevance_threshold" in analysis_cfg), 0.2)

        for analysis_cls in analyses_to_run:
            analyzer = analysis_cls()
            func = analyzer.analyze
            if apply_relevance and lower_limit is not None and upper_limit is not None:
                func = relevance_decorator(
                    lower_limit,
                    upper_limit,
                    relevance_threshold,
                )(func)
            result = func(df, group_col, value_col)
            result['column'] = value_col
            results.append(result)
            logging.info(f"{analysis_cls.__name__} for {value_col}: {result}")

        # Create a subplot figure with 1 row and 2 columns
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Box Plot", "Cumulative Frequency"))

        # Add box plot to the first column
        plotter = ConfigLoader("config.yaml").get_plot_instance("BoxPlot")
        plotter.plot(df, group_col, value_col, lower_limit, upper_limit, fig=fig, row=1, col=1)

        # Add cumulative frequency plot to the second column
        plotter = ConfigLoader("config.yaml").get_plot_instance("CumulativeFrequencyPlot")
        plotter.plot(df, group_col, value_col, lower_limit, upper_limit, fig=fig, row=1, col=2)

        fig.update_layout(title_text=f"Plots for {value_col}")
        plots[value_col] = fig

    return plots, results

def generate_reports(plots: Dict, results: List[Dict], config: Dict) -> None:
    """
    Generate reports based on the provided plots and configuration.

    :param plots: A dictionary of generated plots.
    :param results: A list of analysis results.
    :param config: The configuration dictionary.
    """
    output_config = config.get("output", {})
    if (
        output_config.get("save_interactive_html")
        or output_config.get("save_static_html")
        or output_config.get("save_pdf")
    ):
        generate_report(plots, results, config)

def main() -> None:
    """
    Main function to run the data analysis and reporting.
    """
    loader = ConfigLoader("config.yaml")
    config = loader.settings

    df, limits = load_data_with_limits("data/fake.csv")

    plots, results = process_columns(df, config, limits)

    generate_reports(plots, results, config)

if __name__ == "__main__":
    main()
