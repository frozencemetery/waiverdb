#!/usr/bin/python

# SPDX-License-Identifier: GPL-2.0+

from waiverdb.app import create_app, init_db

if __name__ == '__main__':
    app = create_app('waiverdb.config.DevelopmentConfig')
    init_db(app)
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG'],
    )
