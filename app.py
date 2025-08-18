import typer
from typing_extensions import Annotated
from pathlib import Path
import importlib.metadata
from typing import Optional
import os

from src.utils.config_loader import ConfigLoader
from src.main import run_analysis

app = typer.Typer()


def version_callback(value: bool):
    if value:
        __version__ = importlib.metadata.version("exan")
        typer.echo(f"exan version: {__version__}")
        raise typer.Exit()


@app.command()
def main(
    data_folder: Annotated[Path, typer.Option("--data-folder", "-d", help="Path to the data folder with a config file or a single csv file.")] = Path("."),
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True, help="Show the application's version and exit."),
    ] = None,
):
    """Run the data analysis and reporting.
    """
    config_file = data_folder / "config.yaml"

    if config_file.exists():
        loader = ConfigLoader(config_file=str(config_file))
        config = loader.settings
        # Make data_file path relative to the data_folder
        if not os.path.isabs(config.input.data_file):
            config.input.data_file = (data_folder / config.input.data_file).resolve()
    else:
        typer.echo("Could not find config.yaml. Looking for a single CSV file.")
        csv_files = list(data_folder.glob("*.csv"))
        if len(csv_files) == 1:
            data_file = csv_files[0]
            typer.echo(f"Found single CSV file: {data_file}")

            # Prompt user for information
            title = typer.prompt("Enter the experiment title")
            group_col = typer.prompt("Enter the group column", default="groups")
            analysis = typer.prompt("Enter the statistical analysis to perform (e.g., TTestAnalysis, AnovaAnalysis)")

            loader = ConfigLoader()
            config = loader.settings

            # Update config with user input
            config.report.name = title
            config.input.data_file = str(data_file)
            config.input.group_col = group_col
            config.analyses = [{"name": analysis}]

        elif len(csv_files) == 0:
            typer.echo("Error: No CSV files found in the data folder.")
            raise typer.Exit(code=1)
        else:
            typer.echo("Error: Multiple CSV files found. Please specify a config.yaml.")
            raise typer.Exit(code=1)

    style_settings = loader.style_settings
    run_analysis(config, style_settings, loader)

if __name__ == "__main__":
    app()
