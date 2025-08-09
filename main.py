from config_loader import ConfigLoader
import logging
import pandas as pd
from relevance_decorator import relevance_decorator

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def main():
    loader = ConfigLoader("config.yaml")
    config = loader.settings
    df = pd.read_csv("data.csv")

    group_col = config.group_col
    value_col = config.value_col
    lower_limit = float(df[config.lower_limit_col].iloc[0])
    upper_limit = float(df[config.upper_limit_col].iloc[0])

    for analysis_cfg in config.analyses:
        analyzer = loader.get_analysis_instance(analysis_cfg.name)
        func = analyzer.analyze
        if getattr(analysis_cfg, "relevance", False):
            func = relevance_decorator(
                lower_limit,
                upper_limit,
                getattr(analysis_cfg, "relevance_threshold", 0.2),
            )(func)
        result = func(df, group_col, value_col)
        logging.info(f"{analysis_cfg.name}: {result}")

    for plot_cfg in config.plots:
        plotter = loader.get_plot_instance(plot_cfg.name)
        plotter.plot(df, group_col, value_col, lower_limit, upper_limit)

if __name__ == "__main__":
    main()
