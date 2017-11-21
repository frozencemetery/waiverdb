# SPDX-License-Identifier: GPL-2.0+

import click
from flask.cli import FlaskGroup


def create_waiver_app(_):
    from waiverdb.app import create_app  # noqa: F401
    return create_app()


@click.group(cls=FlaskGroup, create_app=create_waiver_app)
def cli():
    pass


if __name__ == '__main__':
    cli()  # pylint: disable=E1120
