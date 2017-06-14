# SPDX-License-Identifier: GPL-2.0+

from waiverdb.app import create_app, init_db
app = create_app()
init_db(app)
