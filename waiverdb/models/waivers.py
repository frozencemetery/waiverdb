
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import datetime
from .base import db


class Waiver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    product_version = db.Column(db.String(200), nullable=False)
    waived = db.Column(db.Boolean, nullable=False, default=False)
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, result_id, username, product_version, waived=False, comment=None):
        self.result_id = result_id
        self.username = username
        self.product_version = product_version
        self.waived = waived
        self.comment = comment

    def __repr__(self):
        return '%s(result_id=%r, username=%r, product_version=%r, waived=%r)' % \
            (self.__class__.__name__, self.result_id, self.username, self.product_version,
             self.waived)
