import typer
from typing_extensions import Annotated
from pathlib import Path
import importlib.metadata
from typing import Optional, List
import os
import pandas as pd

from src.utils.config_loader import ConfigLoader
from src.main import run_analysis
from src.utils.types_custom import Config
from src.utils.preprocessing import load_data_with_limits

app = typer.Typer()


def select_data_folder(data_folder_str: str) -> Path:
    """Prompts the user to select a data folder."""
    if not data_folder_str:
        data_folder_str = typer.prompt("Please enter the path to the data folder")

    data_folder = Path(data_folder_str)
    while not data_folder.is_dir():
        typer.echo(f"Error: '{data_folder}' is not a valid directory.")
        data_folder_str = typer.prompt("Please enter a valid path to the data folder")
        data_folder = Path(data_folder_str)
    return data_folder

def find_csv_file(data_folder: Path) -> Path:
    """Finds the CSV file to use."""
    csv_files = list(data_folder.glob("*.csv"))
    if len(csv_files) == 1:
        return csv_files[0]
    elif len(csv_files) == 0:
        typer.echo("Error: No CSV files found in the data folder.")
        raise typer.Exit(code=1)
    else:
        typer.echo("Multiple CSV files found. Please select one:")
        for i, f in enumerate(csv_files):
            typer.echo(f"[{i+1}] {f.name}")

        choice = typer.prompt("Enter the number of the file to use", type=int)

        if not 1 <= choice <= len(csv_files):
            typer.echo("Error: Invalid choice.")
            raise typer.Exit(code=1)

        return csv_files[choice - 1]

def load_and_validate_config(config_file: Optional[Path], data_folder: Path, csv_file: Optional[Path]) -> tuple[Config, ConfigLoader]:
    """Loads and validates the configuration."""
    if config_file and config_file.exists():
        loader = ConfigLoader(config_file=str(config_file))
        config = loader.settings
        if not os.path.isabs(config.input.data_file):
            config.input.data_file = (data_folder / config.input.data_file).resolve()
    else:
        typer.echo("Could not find config.yaml. Starting interactive configuration.")
        csv_file = find_csv_file(data_folder)
        typer.echo(f"Using data file: {csv_file}")

        loader = ConfigLoader()
        config = loader.settings
        config.input.data_file = str(csv_file)

    if not config.report.get("name"):
        config.report.name = typer.prompt("Enter the experiment title")

    if not config.input.get("group_col"):
        config.input.group_col = typer.prompt("Enter the group column", default="groups")

    if not config.get("analyses"):
        analysis = typer.prompt("Enter the statistical analysis to perform (e.g., TTestAnalysis, AnovaAnalysis)")
        config.analyses = [{"name": analysis}]

    if not config.output.get("save_interactive_html") and not config.output.get("save_static_html") and not config.output.get("save_pdf"):
        config.output.save_interactive_html = typer.confirm("Save interactive HTML report?")
        config.output.save_static_html = typer.confirm("Save static HTML report?")
        config.output.save_pdf = typer.confirm("Save PDF report?")

    config.output.output_directory = str(data_folder)
    return config, loader

def validate_group_column(df: pd.DataFrame, config: Config) -> None:
    """Validates the group column."""
    if config.input.group_col not in df.columns:
        typer.echo(f"Error: Group column '{config.input.group_col}' not found in the data file.")
        typer.echo("Available columns are:")
        for col in df.columns:
            typer.echo(f"- {col}")

        new_group_col = typer.prompt("Please enter the correct group column name")
        if new_group_col not in df.columns:
            typer.echo("Error: Invalid column name.")
            raise typer.Exit(code=1)
        config.input.group_col = new_group_col


def version_callback(value: bool):
    if value:
        __version__ = importlib.metadata.version("exan")
        typer.echo(f"exan version: {__version__}")
        raise typer.Exit()


@app.command()
def main(
    data_folder_str: Annotated[str, typer.Option("--data-folder", "-d", help="Path to the data folder with a config file or a single csv file.")] = "",
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True, help="Show the application's version and exit."),
    ] = None,
):
    """Run the data analysis and reporting.
    """
    data_folder = select_data_folder(data_folder_str)
    config_file = data_folder / "config.yaml"

    config, loader = load_and_validate_config(config_file, data_folder, None)

    df, _ = load_data_with_limits(config.input.data_file)
    validate_group_column(df, config)

    style_settings = loader.style_settings
    run_analysis(config, style_settings, loader)

if __name__ == "__main__":
    app()
