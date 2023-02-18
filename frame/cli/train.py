import typer

from frame.utils import get_logger

logger = get_logger(__name__)

cli = typer.Typer()

# TODO


@cli.command()
def eta():
    pass


@cli.command()
def availability():
    pass
