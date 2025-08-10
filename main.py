from utils.config_loader import ConfigLoader
import logging
import pandas as pd
from utils.relevance_decorator import relevance_decorator
from utils.analyses import AnovaAnalysis, TTestAnalysis, MannWhitneyAnalysis

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def main():
    loader = ConfigLoader("config.yaml")
    config = loader.settings
    df = pd.read_csv("data/fake.csv")

    group_col = config['group_col']
    value_col = config['value_col']
    lower_limit = float(df[config['lower_limit_col']].iloc[0])
    upper_limit = float(df[config['upper_limit_col']].iloc[0])

    num_groups = df[group_col].nunique()
    analyses_to_run = []
    if num_groups == 2:
        analyses_to_run = [TTestAnalysis, MannWhitneyAnalysis]
    elif num_groups > 2:
        analyses_to_run = [AnovaAnalysis]

    # Check if relevance decorator should be applied
    apply_relevance = any(analysis_cfg.get("relevance", False) for analysis_cfg in config['analyses'])
    relevance_threshold = next((analysis_cfg.get("relevance_threshold", 0.2) for analysis_cfg in config['analyses'] if "relevance_threshold" in analysis_cfg), 0.2)


    for analysis_cls in analyses_to_run:
        analyzer = analysis_cls()
        func = analyzer.analyze
        if apply_relevance:
            func = relevance_decorator(
                lower_limit,
                upper_limit,
                relevance_threshold,
            )(func)
        result = func(df, group_col, value_col)
        logging.info(f"{analysis_cls.__name__}: {result}")

    output_config = config.get('output', {})
    for plot_cfg in config['plots']:
        plotter = loader.get_plot_instance(plot_cfg['name'])
        plotter.plot(df, group_col, value_col, lower_limit, upper_limit, output_config=output_config)

if __name__ == "__main__":
    main()
