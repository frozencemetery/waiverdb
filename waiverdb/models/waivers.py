# SPDX-License-Identifier: GPL-2.0+

import datetime
from .base import db
from sqlalchemy import or_, and_
from sqlalchemy.dialects.postgresql import JSONB


class Waiver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, nullable=True)
    subject = db.Column(JSONB, nullable=False, index=True)
    testcase = db.Column(db.Text, nullable=False, index=True)
    username = db.Column(db.String(255), nullable=False)
    proxied_by = db.Column(db.String(255))
    product_version = db.Column(db.String(200), nullable=False)
    waived = db.Column(db.Boolean, nullable=False, default=False)
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, subject, testcase, username, product_version, waived=False,
                 comment=None, proxied_by=None):
        self.subject = subject
        self.testcase = testcase
        self.username = username
        self.product_version = product_version
        self.waived = waived
        self.comment = comment
        self.proxied_by = proxied_by

    def __repr__(self):
        return '%s(result_id=%r, subject=%r, testcase=%r, username=%r, product_version=%r,\
                waived=%r)' % (self.__class__.__name__, self.result_id, self.subject, self.testcase,
                               self.username, self.product_version, self.waived)

    @classmethod
    def by_results(cls, query, results):
        return query.filter(or_(*[
            and_(
                cls.subject == d['subject'],
                cls.testcase == d['testcase']
            ) if d.get('testcase', None) else
            and_(
                cls.subject == d['subject']
            ) if d.get('subject', None) else
            and_() for d in results
        ]))
