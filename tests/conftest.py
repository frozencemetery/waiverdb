# SPDX-License-Identifier: GPL-2.0+

from copy import copy
import pytest
from sqlalchemy import create_engine
from waiverdb.app import create_app


@pytest.fixture(scope='session')
def app(request):
    app = create_app('waiverdb.config.TestingConfig')
    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app):
    """Session-wide test database."""
    from waiverdb.models import db
    dbname = db.engine.url.database
    # In order to drop and re-create the database, we have to connect to
    # template1 database in special AUTOCOMMIT isolation level.
    dburl = copy(db.engine.url)
    dburl.database = 'template1'
    with create_engine(dburl).connect() as connection:
        connection.execution_options(isolation_level='AUTOCOMMIT')
        connection.execute('DROP DATABASE IF EXISTS {}'.format(dbname))
        connection.execute('CREATE DATABASE {}'.format(dbname))
    db.create_all()
    return db


@pytest.yield_fixture
def session(db, monkeypatch):
    """Patch Flask-SQLAlchemy to use a specific connection"""
    connection = db.engine.connect()
    transaction = connection.begin()

    # Patch Flask-SQLAlchemy to use our connection
    monkeypatch.setattr(db, 'get_engine', lambda *args: connection)

    yield db.session

    db.session.remove()
    transaction.rollback()
    connection.close()


@pytest.yield_fixture
def client(app):
    """A Flask test client. An instance of :class:`flask.testing.TestClient`
    by default.
    """
    with app.test_client() as client:
        yield client


@pytest.fixture()
def enable_kerberos(app, monkeypatch):
    monkeypatch.setitem(app.config, 'AUTH_METHOD', 'Kerberos')


@pytest.fixture()
def enable_ssl(app, monkeypatch):
    monkeypatch.setitem(app.config, 'AUTH_METHOD', 'SSL')
