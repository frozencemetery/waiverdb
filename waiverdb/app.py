# SPDX-License-Identifier: GPL-2.0+

import os
import urlparse

from flask import Flask
from sqlalchemy import event

from waiverdb.events import publish_new_waiver
from waiverdb.logger import init_logging
from waiverdb.api_v1 import api_v1
from waiverdb.models import db
from flask_oidc import OpenIDConnect


def load_config(app):
    # Load default config, then override that with a config file
    if os.getenv('DEV') == 'true':
        default_config_obj = 'waiverdb.config.DevelopmentConfig'
        default_config_file = os.getcwd() + '/conf/settings.py'
    elif os.getenv('TEST') == 'true':
        default_config_obj = 'waiverdb.config.TestingConfig'
        default_config_file = os.getcwd() + '/conf/settings.py'
    else:
        default_config_obj = 'waiverdb.config.ProductionConfig'
        default_config_file = '/etc/waiverdb/settings.py'
    app.config.from_object(default_config_obj)
    config_file = os.environ.get('WAIVERDB_CONFIG', default_config_file)
    app.config.from_pyfile(config_file)
    if os.environ.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.environ['SECRET_KEY']


def populate_db_config(app):
    # Take the application-level DATABASE_URI setting, plus (optionally)
    # a DATABASE_PASSWORD from the environment, and munge them together into
    # the SQLALCHEMY_DATABASE_URI setting which is obeyed by Flask-SQLAlchemy.
    dburi = app.config['DATABASE_URI']
    if os.environ.get('DATABASE_PASSWORD'):
        parsed = urlparse.urlparse(dburi)
        netloc = '{}:{}@{}'.format(parsed.username,
                                   os.environ['DATABASE_PASSWORD'],
                                   parsed.hostname)
        if parsed.port:
            netloc += ':{}'.format(parsed.port)
        dburi = urlparse.urlunsplit(
            (parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
    if app.config['SHOW_DB_URI']:
        app.logger.debug('using DBURI: %s', dburi)
    app.config['SQLALCHEMY_DATABASE_URI'] = dburi


# applicaiton factory http://flask.pocoo.org/docs/0.12/patterns/appfactories/
def create_app(config_obj=None):
    app = Flask(__name__)
    if config_obj:
        app.config.from_object(config_obj)
    else:
        load_config(app)
    if app.config['PRODUCTION'] and app.secret_key == 'replace-me-with-something-random':
        raise Warning("You need to change the app.secret_key value for production")
    populate_db_config(app)
    if app.config['AUTH_METHOD'] == 'OIDC':
        app.oidc = OpenIDConnect(app)
    # initialize db
    db.init_app(app)
    # initialize logging
    init_logging(app)
    # register blueprints
    app.register_blueprint(api_v1, url_prefix="/api/v1.0")
    app.add_url_rule('/healthcheck', view_func=healthcheck)
    register_event_handlers(app)
    return app


def init_db(app):
    with app.app_context():
        db.create_all()
    return db


def healthcheck():
    """
    Request handler for performing an application-level health check. This is
    not part of the published API, it is intended for use by OpenShift or other
    monitoring tools.

    Returns a 200 response if the application is alive and able to serve requests.
    """
    result = db.session.execute('SELECT 1').scalar()
    assert result == 1
    return ('Health check OK', 200, [('Content-Type', 'text/plain')])


def register_event_handlers(app):
    """
    Register SQLAlchemy event handlers with the application's session factory.

    Args:
        app (flask.Flask): The Flask object with the configured scoped session
            attached as the ``session`` attribute.
    """
    if app.config['MESSAGE_BUS_PUBLISH']:
        # A workaround for https://github.com/mitsuhiko/flask-sqlalchemy/pull/364
        # can be removed after python-flask-sqlalchemy is upgraded to 2.2
        from flask_sqlalchemy import SignallingSession
        event.listen(SignallingSession, 'after_commit', publish_new_waiver)
