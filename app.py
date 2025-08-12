import typer
from typing_extensions import Annotated
from pathlib import Path
import importlib.metadata
from typing import Optional

from src.utils.config_loader import ConfigLoader
from src.main import run_analysis # This will be the refactored main function

app = typer.Typer()


def version_callback(value: bool):
    if value:
        __version__ = importlib.metadata.version("exan")
        typer.echo(f"exan version: {__version__}")
        raise typer.Exit()


@app.command()
def main(
    config_file: Annotated[Path, typer.Option("--config", "-c", help="Path to the configuration file.")] = Path("config.yaml"),
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True, help="Show the application's version and exit."),
    ] = None,
):
    """Run the data analysis and reporting.
    """
    loader = ConfigLoader(config_file=str(config_file))
    config = loader.settings
    style_settings = loader.style_settings
    run_analysis(config, style_settings, loader)

if __name__ == "__main__":
    app()
