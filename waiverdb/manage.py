# SPDX-License-Identifier: GPL-2.0+

import time
import click
from flask.cli import FlaskGroup
from sqlalchemy.exc import OperationalError
from waiverdb.models import db


def create_waiver_app(_):
    from waiverdb.app import create_app  # noqa: F401
    return create_app()


@click.group(cls=FlaskGroup, create_app=create_waiver_app)
def cli():
    pass


@cli.command(name='wait-for-db')
def wait_for_db():
    """
    Wait until database server is reachable.
    """
    poll_interval = 10  # seconds
    while True:
        try:
            db.engine.connect()
        except OperationalError as e:
            click.echo('Failed to connect to database: {}'.format(e))
            click.echo('Sleeping for {} seconds...'.format(poll_interval))
            time.sleep(poll_interval)
            click.echo('Retrying...')
        else:
            break


if __name__ == '__main__':
    cli()  # pylint: disable=E1120
