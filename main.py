from utils.config_loader import ConfigLoader
import logging
import pandas as pd
from utils.relevance_decorator import relevance_decorator
from utils.analyses import AnovaAnalysis, TTestAnalysis, MannWhitneyAnalysis
from utils.reporting import generate_report

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def main() -> None:
    loader = ConfigLoader("config.yaml")
    config = loader.settings

    limits = {}
    with open("data/fake.csv", "r") as f:
        for _ in range(2):  # Read the first two lines for limits
            line = f.readline()
            parts = line.strip().split(",")
            if len(parts) == 2:
                limit_name, limit_value = parts
                limits[limit_name] = float(limit_value)

    df = pd.read_csv("data/fake.csv", skiprows=2)

    group_col = config.group_col
    value_cols = [col for col in df.columns if col != group_col]

    plots = {}
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

        # Check if relevance decorator should be applied
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
            logging.info(f"{analysis_cls.__name__} for {value_col}: {result}")

        for plot_cfg in config.plots:
            plot_name = f"{plot_cfg.name}_{value_col}"
            plotter = loader.get_plot_instance(plot_cfg.name)
            fig = plotter.plot(df, group_col, value_col, lower_limit, upper_limit)
            plots[plot_name] = fig

        output_config = config.get("output", {})
        if (
            output_config.get("save_interactive_html")
            or output_config.get("save_static_html")
            or output_config.get("save_pdf")
        ):
            generate_report(plots, config)

    output_config = config.get("output", {})
    if (
        output_config.get("save_interactive_html")
        or output_config.get("save_static_html")
        or output_config.get("save_pdf")
    ):
        generate_report(plots, config)

if __name__ == "__main__":
    main()
