from src.utils.config_loader import ConfigLoader
import logging
import pandas as pd
from src.utils.relevance_decorator import relevance_decorator
from src.utils.analyses import AnovaAnalysis, TTestAnalysis, MannWhitneyAnalysis
from src.utils.reporting import generate_report as _generate_report_actual # Renamed to avoid shadowing
from src.utils.preprocessing import load_data_with_limits
from typing import Tuple, cast, Dict, Optional
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from src.utils.types_custom import Config, AnalysisConfig, PlotConfig, AnalysisResult, OutputConfig
from box import Box # Import Box for style_settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def process_columns(df: pd.DataFrame, config: Config, all_limits: Dict[str, Dict[str, float]], style_settings: Box, loader: ConfigLoader) -> Tuple[dict[str, go.Figure], list[AnalysisResult]]:
    """
    Process each value column in the DataFrame, performing analyses and generating plots.

    :param df: The input DataFrame.
    :param config: The configuration dictionary.
    :nparam all_limits: A dictionary of all limits (per column).
    :param style_settings: The style configuration for plots.
    :param loader: The config loader instance.
    :return: A tuple containing a dictionary of generated plots and a list of analysis results.
    """
    group_col: str = config.input.group_col
    value_cols: list[str] = [
        col for col in df.select_dtypes(include=['number']).columns
        if col != group_col
    ]
    plots: dict[str, go.Figure] = {}
    results: list[AnalysisResult] = []

    for value_col in value_cols:
        logging.info(f"Processing column: {value_col}")

        # Construct limits for the current value_col
        limits: Dict[str, Optional[float]] = {
            "lower_limit": all_limits.get("Lower_Limit", {}).get(value_col),
            "upper_limit": all_limits.get("Upper_Limit", {}).get(value_col),
            "target_value": all_limits.get("Target", {}).get(value_col),
        }

        num_groups: int = df[group_col].nunique()
        analyses_to_run: list = []
        if num_groups == 2:
            analyses_to_run = [TTestAnalysis, MannWhitneyAnalysis]
        elif num_groups > 2:
            analyses_to_run = [AnovaAnalysis]

        apply_relevance: bool = any(cast(AnalysisConfig, analysis_cfg)["relevance"] for analysis_cfg in config["analyses"])
        relevance_threshold: float = next((cast(AnalysisConfig, analysis_cfg)["relevance_threshold"] for analysis_cfg in config["analyses"] if "relevance_threshold" in analysis_cfg), 0.2)

        # Initialize result with default None values to prevent UnboundLocalError
        result: AnalysisResult = {'p_value': None, 'test': None, 'F_statistic': None, 'statistic': None}

        for analysis_cls in analyses_to_run:
            analyzer = analysis_cls()
            func = analyzer.analyze
            if apply_relevance and limits["lower_limit"] is not None and limits["upper_limit"] is not None:
                func = relevance_decorator(
                    limits, # Pass limits
                    relevance_threshold,
                )(func)
            result: AnalysisResult = func(df, group_col, value_col)
            result['column'] = value_col # pyright: ignore[reportGeneralTypeIssues]
            results.append(result)
            logging.info(f"{analysis_cls.__name__} for {value_col}: {result}")

        # Retrieve statistical values for subplot titles
        p_value = result.get('p_value')
        test_name = result.get('test')
        statistic_value = None
        if test_name == 'ANOVA':
            statistic_value = result.get('F_statistic')
        else:
            statistic_value = result.get('statistic')

        # Create a subplot figure with 1 row and 2 columns
        box_plot_title = f"Box Plot (P={p_value:.3f}, Stat={statistic_value:.3f})" if p_value is not None and statistic_value is not None else "Box Plot"
        cumulative_frequency_title = f"Cumulative Frequency (P={p_value:.3f}, Stat={statistic_value:.3f})" if p_value is not None and statistic_value is not None else "Cumulative Frequency"
        fig: go.Figure = make_subplots(rows=1, cols=2, subplot_titles=(box_plot_title, cumulative_frequency_title))

        # Add box plot to the first column
        plotter = loader.get_plot_instance("BoxPlot")
        plotter.plot(df, group_col, value_col, limits=limits, fig=fig, row=1, col=1, style_settings=style_settings, results=results)

        # Add cumulative frequency plot to the second column
        plotter = loader.get_plot_instance("CumulativeFrequencyPlot")
        plotter.plot(df, group_col, value_col, limits=limits, fig=fig, row=1, col=2, style_settings=style_settings, results=results)

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

def run_analysis(config: Config, style_settings: Box, loader: ConfigLoader) -> None:
    """
    Main function to run the data analysis and reporting.
    """
    df, all_limits = load_data_with_limits(config.input.data_file)

    plots: dict[str, go.Figure]
    results: list[AnalysisResult]
    plots, results = process_columns(df, config, all_limits, style_settings, loader)

    # Generate significance plot
    if any(cast(PlotConfig, plot_cfg)["name"] == "SignificancePlot" for plot_cfg in config["plots"]):
        plotter = loader.get_plot_instance("SignificancePlot")
        # Pass df, group_col, value_col as required by ABC, even if unused by SignificancePlot
        # Pass a dummy limits dict for SignificancePlot as it doesn't use it directly
        fig: go.Figure = plotter.plot(df=df, group_col=config.input.group_col, value_col=config.input.value_col, limits={}, results=results, style_settings=style_settings)
        plots["Significance Plot"] = fig

    generate_reports(plots, results, config)

