# SPDX-License-Identifier: GPL-2.0+

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
