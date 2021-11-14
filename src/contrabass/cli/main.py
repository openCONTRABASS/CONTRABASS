from __future__ import absolute_import

import click

__version__ = "0.0.0"

from .commands import report, new_model


@click.group()
@click.help_option("--help", "-h")
@click.version_option(__version__, "--version", "-V")
def contrabass():
    """
    Compute vulnerabilities on constrained-based models
    """
    pass


contrabass.add_command(report)
contrabass.add_command(new_model)


if __name__ == "__main__":
    contrabass()
