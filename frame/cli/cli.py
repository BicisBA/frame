import logging

import typer
import uvicorn

from frame.cli.train import cli as train_cli
from frame.cli.stations import cli as stations_cli
from frame.utils import DEFAULT_PRETTY, DEFAULT_VERBOSE, config_logging

cli = typer.Typer()
cli.add_typer(stations_cli, name="stations")
cli.add_typer(train_cli, name="train")


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


@cli.command()
def server(
    host: str = typer.Option("127.0.0.1", help="Host to bind to"),
    port: int = typer.Option(10101, help="Port to bind to"),
    reload: bool = typer.Option(False, help="Live reloading"),
    workers: int = typer.Option(2, min=1, help="Amount of workers to use"),
):
    uvicorn_server = uvicorn.Server(
        uvicorn.Config(
            "frame.api.app:app",
            reload=reload,
            host=host,
            port=port,
            workers=workers,
            log_level=logging.getLevelName(
                logging.getLogger().getEffectiveLevel()
            ).lower(),
        )
    )

    uvicorn_server.run()
