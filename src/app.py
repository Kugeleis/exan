import typer
from typing_extensions import Annotated
from pathlib import Path

from src.utils.config_loader import ConfigLoader
from src.main import run_analysis # This will be the refactored main function

app = typer.Typer()

@app.command()
def main(
    config_file: Annotated[Path, typer.Option("--config", "-c", help="Path to the configuration file.")] = Path("config.yaml"),
):
    """Run the data analysis and reporting.
    """
    loader = ConfigLoader(config_file=str(config_file))
    config = loader.settings
    style_settings = loader.style_settings
    run_analysis(config, style_settings, loader)

if __name__ == "__main__":
    app()
