from utils.config_loader import ConfigLoader
import logging
import pandas as pd
from utils.relevance_decorator import relevance_decorator
from utils.analyses import AnovaAnalysis, TTestAnalysis, MannWhitneyAnalysis
from utils.reporting import generate_report as _generate_report_actual # Renamed to avoid shadowing
from utils.preprocessing import load_data_with_limits
from typing import Tuple, cast
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from utils.types_custom import Config, AnalysisConfig, PlotConfig, AnalysisResult, OutputConfig

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def process_columns(df: pd.DataFrame, config: Config, limits: dict[str, float]) -> Tuple[dict[str, go.Figure], list[AnalysisResult]]:
    """
    Process each value column in the DataFrame, performing analyses and generating plots.

    :param df: The input DataFrame.
    :param config: The configuration dictionary.
    :param limits: A dictionary of limits.
    :return: A tuple containing a dictionary of generated plots and a list of analysis results.
    """
    group_col: str = config["group_col"]
    value_cols: list[str] = [col for col in df.columns if col != group_col]
    plots: dict[str, go.Figure] = {}
    results: list[AnalysisResult] = []

    for value_col in value_cols:
        logging.info(f"Processing column: {value_col}")

        lower_limit: float | None = limits.get(f"{value_col}_Lower_Limit")
        upper_limit: float | None = limits.get(f"{value_col}_Upper_Limit")
        target_value: float | None = limits.get(f"{value_col}_Target") # Get target value

        num_groups: int = df[group_col].nunique()
        analyses_to_run: list = []
        if num_groups == 2:
            analyses_to_run = [TTestAnalysis, MannWhitneyAnalysis]
        elif num_groups > 2:
            analyses_to_run = [AnovaAnalysis]

        apply_relevance: bool = any(cast(AnalysisConfig, analysis_cfg)["relevance"] for analysis_cfg in config["analyses"])
        relevance_threshold: float = next((cast(AnalysisConfig, analysis_cfg)["relevance_threshold"] for analysis_cfg in config["analyses"] if "relevance_threshold" in analysis_cfg), 0.2)

        for analysis_cls in analyses_to_run:
            analyzer = analysis_cls()
            func = analyzer.analyze
            if apply_relevance and lower_limit is not None and upper_limit is not None:
                func = relevance_decorator(
                    lower_limit,
                    upper_limit,
                    relevance_threshold,
                )(func)
            result: AnalysisResult = func(df, group_col, value_col)
            result['column'] = value_col # pyright: ignore[reportGeneralTypeIssues]
            results.append(result)
            logging.info(f"{analysis_cls.__name__} for {value_col}: {result}")

        # Create a subplot figure with 1 row and 2 columns
        fig: go.Figure = make_subplots(rows=1, cols=2, subplot_titles=("Box Plot", "Cumulative Frequency"))

        # Add box plot to the first column
        plotter = ConfigLoader("config.yaml").get_plot_instance("BoxPlot")
        plotter.plot(df, group_col, value_col, lower_limit, upper_limit, target_value, fig=fig, row=1, col=1)

        # Add cumulative frequency plot to the second column
        plotter = ConfigLoader("config.yaml").get_plot_instance("CumulativeFrequencyPlot")
        plotter.plot(df, group_col, value_col, lower_limit, upper_limit, target_value, fig=fig, row=1, col=2)

        fig.update_layout(title_text=f"Plots for {value_col}")
        plots[value_col] = fig

    return plots, results

def generate_reports(plots: dict[str, go.Figure], results: list[AnalysisResult], config: Config) -> None:
    """
    Generate reports based on the provided plots and configuration.

    :param plots: A dictionary of generated plots.
    :param results: A list of analysis results.
    :param config: The configuration dictionary.
    """
    output_config: OutputConfig = config["output"]
    if (
        output_config.get("save_interactive_html")
        or output_config.get("save_static_html")
        or output_config.get("save_pdf")
    ):
        _generate_report_actual(plots, results, config)

def main() -> None:
    """
    Main function to run the data analysis and reporting.
    """
    loader = ConfigLoader("config.yaml")
    config: Config = loader.settings

    df, limits = load_data_with_limits("data/fake.csv")

    plots: dict[str, go.Figure]
    results: list[AnalysisResult]
    plots, results = process_columns(df, config, limits)

    # Generate significance plot
    if any(cast(PlotConfig, plot_cfg)["name"] == "SignificancePlot" for plot_cfg in config["plots"]):
        plotter = loader.get_plot_instance("SignificancePlot")
        fig: go.Figure = plotter.plot(results=results)
        plots["Significance Plot"] = fig

    generate_reports(plots, results, config)

if __name__ == "__main__":
    main()