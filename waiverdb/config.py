
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


class Config(object):
    """
    A WaiverDB Flask configuration.

    Attributes:
        ZEROMQ_PUBLISH (bool): When true, ZeroMQ messages will be emitted via
            fedmsg when new waivers are created.
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    JOURNAL_LOGGING = False
    HOST = '0.0.0.0'
    PORT = 5004
    PRODUCTION = False
    SHOW_DB_URI = False
    SECRET_KEY = 'replace-me-with-something-random'
    # need to explicitly turn this off
    # https://github.com/flask-restful/flask-restful/issues/449
    ERROR_404_HELP = False
    AUTH_METHOD = 'OIDC'  # Specify OIDC or Kerberos for authentication
    # Change it if the Kerberos service is not running on which the waiverdb is run.
    KERBEROS_HTTP_HOST = None
    ZEROMQ_PUBLISH = True


class ProductionConfig(Config):
    DEBUG = False
    PRODUCTION = True


class DevelopmentConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TRAP_BAD_REQUEST_ERRORS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////var/tmp/waiverdb_db.sqlite'
    SHOW_DB_URI = True
    # The location of the client_secrets.json file used for API authentication
    OIDC_CLIENT_SECRETS = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'conf',
        'client_secrets.json'
    )
    OIDC_REQUIRED_SCOPE = 'https://waiverdb.fedoraproject.org/oidc/create-waiver'
    OIDC_RESOURCE_SERVER_ONLY = True


class TestingConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TRAP_BAD_REQUEST_ERRORS = True
    TESTING = True
    OIDC_CLIENT_SECRETS = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tests',
        'client_secrets.json'
    )
    OIDC_REQUIRED_SCOPE = 'waiverdb_scope'
    OIDC_RESOURCE_SERVER_ONLY = True
