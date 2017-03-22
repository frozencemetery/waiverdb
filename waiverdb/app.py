
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import os

from flask import Flask
from sqlalchemy import event

from waiverdb.events import fedmsg_new_waiver
from waiverdb.logger import init_logging
from waiverdb.api_v1 import api_v1
from waiverdb.models import db
from flask_oidc import OpenIDConnect


def load_default_config(app):
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
    if os.path.exists(config_file):
        app.config.from_pyfile(config_file)


# applicaiton factory http://flask.pocoo.org/docs/0.12/patterns/appfactories/
def create_app(config_obj=None):
    app = Flask(__name__)
    if config_obj:
        app.config.from_object(config_obj)
    else:
        load_default_config(app)
    if app.config['PRODUCTION'] and app.secret_key == 'replace-me-with-something-random':
        raise Warning("You need to change the app.secret_key value for production")
    if app.config['SHOW_DB_URI']:
        app.logger.debug('using DBURI: %s' % app.config['SQLALCHEMY_DATABASE_URI'])
    if app.config['AUTH_METHOD'] == 'OIDC':
        app.oidc = OpenIDConnect(app)
    # initialize db
    db.init_app(app)
    # initialize logging
    init_logging(app)
    # register blueprints
    app.register_blueprint(api_v1, url_prefix="/api/v1.0")
    register_event_handlers(app)
    return app


def init_db(app):
    with app.app_context():
        db.create_all()
    return db


def register_event_handlers(app):
    """
    Register SQLAlchemy event handlers with the application's session factory.

    Args:
        app (flask.Flask): The Flask object with the configured scoped session
            attached as the ``session`` attribute.
    """
    if app.config['ZEROMQ_PUBLISH']:
        # A workaround for https://github.com/mitsuhiko/flask-sqlalchemy/pull/364
        # can be removed after python-flask-sqlalchemy is upgraded to 2.2
        from flask_sqlalchemy import SignallingSession
        event.listen(SignallingSession, 'after_commit', fedmsg_new_waiver)
