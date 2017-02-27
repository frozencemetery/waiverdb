
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

import os
import pytest

from waiverdb.app import create_app, init_db

@pytest.fixture(scope='session')
def app(tmpdir_factory, request):
    app = create_app('waiverdb.config.TestingConfig')
    db_file = tmpdir_factory.mktemp('waiverdb').join('db.sqlite')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_file
    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app

@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    db = init_db(app)
    def teardown():
        db.drop_all()
    request.addfinalizer(teardown)
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
