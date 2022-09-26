import typer

from frame.cli.stations import cli as stations_cli
from frame.utils import DEFAULT_PRETTY, DEFAULT_VERBOSE, config_logging

cli = typer.Typer()
cli.add_typer(stations_cli, name="stations")


@cli.callback()
def main(
    verbose: int = typer.Option(
        DEFAULT_VERBOSE,
        "--verbose",
        "-v",
        count=True,
        help="Level of verbosity. Can be passed more than once for more levels of logging.",
    ),
    pretty: bool = typer.Option(
        DEFAULT_PRETTY, "--pretty", help="Whether to pretty print the logs with colors"
    ),
):
    config_logging(verbose, pretty)
